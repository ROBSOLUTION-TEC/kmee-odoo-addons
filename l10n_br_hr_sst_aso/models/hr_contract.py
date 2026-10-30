# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .hr_employee_medical_examination import TIPO_ASO_ADMISSIONAL, TIPO_ASO_DEMISSIONAL

# NR-7, item 7.5.11: o demissional é feito em até 10 dias contados do término
# do contrato e pode ser dispensado se o exame clínico ocupacional mais recente
# tiver menos de 135 dias (graus de risco 1 e 2 da NR-4) ou de 90 dias (graus 3
# e 4). Sem grau informado, vale o prazo mais restritivo.
PRAZO_DEMISSIONAL_DIAS = 10
DISPENSA_DEMISSIONAL_DIAS = {"1": 135, "2": 135, "3": 90, "4": 90}
DISPENSA_DEMISSIONAL_PADRAO = 90

SITUACAO_DEMISSIONAL = [
    ("dispensado", "Dispensado (NR-7, item 7.5.11)"),
    ("cobrado", "Cobrado"),
    ("realizado", "Realizado"),
]


class HrContract(models.Model):
    # Odoo 19+: hr.contract foi incorporado a hr.version
    _inherit = "hr.version"

    l10n_br_sst_demissional = fields.Selection(
        SITUACAO_DEMISSIONAL,
        string="Exame Demissional",
        readonly=True,
        copy=False,
        tracking=True,
        help="Situação do exame demissional depois do encerramento do "
        "contrato. Cobrado significa que há atividade com prazo no término "
        "mais 10 dias (NR-7, item 7.5.11).",
    )

    def _l10n_br_sst_exige_aso(self, tipo_codigo):
        """Verifica o ASO exigido e aplica a política da empresa.

        Só o admissional passa por aqui: a NR-7 exige que ele seja feito antes
        de o empregado assumir as atividades (item 7.5.8, I). Empresa que ainda
        não tem o processo redondo pode se contentar com o alerta, e é esse o
        padrão: bloquear a admissão de quem já foi contratado costuma travar a
        folha, não proteger ninguém.
        """
        self.ensure_one()
        politica = self.company_id.l10n_br_sst_aso_politica
        if politica == "ignora":
            return True
        # sudo: a regra de acesso do exame limita o usuário comum aos próprios
        # exames, e quem abre ou encerra o contrato não os enxergaria. Só a
        # existência do ASO interessa aqui, nunca o conteúdo.
        exame = (
            self.env["hr.employee.medical.examination"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("l10n_br_tipo_aso_codigo", "=", tipo_codigo),
                    ("state", "=", "done"),
                ],
                limit=1,
            )
        )
        if exame:
            return True
        rotulos = {
            TIPO_ASO_ADMISSIONAL: _("admissional"),
            TIPO_ASO_DEMISSIONAL: _("demissional"),
        }
        mensagem = _(
            "O trabalhador %(nome)s não tem ASO %(tipo)s concluído, exigido "
            "pela NR-7."
        ) % {
            "nome": self.employee_id.name,
            "tipo": rotulos.get(tipo_codigo, tipo_codigo),
        }
        if politica == "bloqueia":
            raise UserError(mensagem)
        self.message_post(body=mensagem)
        return False

    def write(self, vals):
        """Checa o ASO admissional na abertura do contrato.

        O encerramento não é checado aqui: o demissional tem prazo de 10 dias
        depois do término e pode ser dispensado (NR-7, item 7.5.11). A cobrança
        é do cron, com atividade no prazo legal.
        """
        # Odoo 20: não há mais estado "em andamento"; a abertura do contrato é
        # o preenchimento do início do contrato na primeira versão.
        sem_inicio = self.filtered(lambda c: not c.contract_date_start)
        res = super().write(vals)
        if vals.get("contract_date_start"):
            for rec in sem_inicio._l10n_br_sst_primeiras_versoes():
                rec._l10n_br_sst_exige_aso(TIPO_ASO_ADMISSIONAL)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super().create(vals_list)
        for contract in contracts.filtered(
            lambda c: c.employee_id and c.contract_date_start
        )._l10n_br_sst_primeiras_versoes():
            contract._l10n_br_sst_exige_aso(TIPO_ASO_ADMISSIONAL)
        return contracts

    def _l10n_br_sst_primeiras_versoes(self):
        """Versões que abrem um contrato (sem versão anterior do mesmo contrato).

        Uma nova versão criada por alteração contratual (ex.: reajuste) não é
        uma admissão e não exige outro ASO admissional.
        """
        return self.filtered(
            lambda v: not v.employee_id.version_ids.filtered(
                lambda o, v=v: o != v
                and o.contract_date_start == v.contract_date_start
                and o.date_version < v.date_version
            )
        )

    def _l10n_br_sst_contrato_encerrado(self, data=None):
        """O contrato terminou (fim do contrato preenchido e já alcançado)."""
        self.ensure_one()
        data = data or fields.Date.context_today(self)
        return bool(self.contract_date_end) and self.contract_date_end <= data

    def _l10n_br_sst_contrato_vigente(self, data=None):
        """O contrato vigora na data (início alcançado e fim não alcançado)."""
        self.ensure_one()
        data = data or fields.Date.context_today(self)
        return bool(self.contract_date_start) and self.contract_date_start <= data and (
            not self.contract_date_end or self.contract_date_end >= data
        )

    def _l10n_br_sst_ultima_versao(self):
        """Só a versão mais recente de cada contrato (uma cobrança por contrato)."""
        return self.filtered(
            lambda v: not v.employee_id.version_ids.filtered(
                lambda o, v=v: o.contract_date_start == v.contract_date_start
                and o.date_version > v.date_version
            )
        )

    # ------------------------------------------------------------------
    # Demissional
    # ------------------------------------------------------------------

    def _l10n_br_sst_termino(self):
        """Data de término do contrato, com queda para a data do encerramento."""
        self.ensure_one()
        return self.contract_date_end or fields.Date.to_date(self.write_date)

    def _l10n_br_sst_exames_concluidos(self, termino):
        # sudo: ver comentário em _l10n_br_sst_exige_aso.
        return (
            self.env["hr.employee.medical.examination"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("state", "=", "done"),
                    ("date", "!=", False),
                    (
                        "date",
                        "<=",
                        termino + relativedelta(days=PRAZO_DEMISSIONAL_DIAS),
                    ),
                ],
                order="date desc, id desc",
            )
        )

    def _l10n_br_sst_dispensa_demissional(self):
        """Avalia a dispensa do demissional do item 7.5.11 da NR-7.

        Returns:
            Tupla ``(dispensado, ultimo_exame, limite_dias)``.
        """
        self.ensure_one()
        termino = self._l10n_br_sst_termino()
        limite = DISPENSA_DEMISSIONAL_DIAS.get(
            self.company_id.l10n_br_sst_grau_risco, DISPENSA_DEMISSIONAL_PADRAO
        )
        ultimo = self._l10n_br_sst_exames_concluidos(termino).filtered(
            lambda e: e.date <= termino
        )[:1]
        dispensado = bool(ultimo) and (termino - ultimo.date).days < limite
        return dispensado, ultimo, limite

    def _l10n_br_sst_demissional_realizado(self):
        self.ensure_one()
        termino = self._l10n_br_sst_termino()
        return self._l10n_br_sst_exames_concluidos(termino).filtered(
            lambda e: e.l10n_br_tipo_aso_codigo == TIPO_ASO_DEMISSIONAL
            and (not self.contract_date_start or e.date >= self.contract_date_start)
        )[:1]

    def l10n_br_sst_cobrar_demissional(self):
        """Dispensa, registra ou cobra o demissional de contratos encerrados.

        Cada contrato é avaliado uma vez: o resultado fica em
        ``l10n_br_sst_demissional``. A cobrança é uma atividade com prazo no
        término mais 10 dias, nunca um bloqueio.
        """
        tipo = self.env.ref("l10n_br_hr_sst_aso.mail_activity_type_aso_demissional")
        for rec in self:
            if (
                not rec._l10n_br_sst_contrato_encerrado()
                or rec.l10n_br_sst_demissional
                or rec.company_id.l10n_br_sst_aso_politica == "ignora"
            ):
                continue
            if rec._l10n_br_sst_demissional_realizado():
                rec.l10n_br_sst_demissional = "realizado"
                continue
            termino = rec._l10n_br_sst_termino()
            dispensado, ultimo, limite = rec._l10n_br_sst_dispensa_demissional()
            if dispensado:
                rec.l10n_br_sst_demissional = "dispensado"
                rec.message_post(
                    body=_(
                        "Exame demissional dispensado (NR-7, item 7.5.11): o "
                        "último exame clínico ocupacional foi em %(data)s, "
                        "%(dias)s dias antes do término, abaixo do limite de "
                        "%(limite)s dias para o grau de risco da empresa."
                    )
                    % {
                        "data": ultimo.date.strftime("%d/%m/%Y"),
                        "dias": (termino - ultimo.date).days,
                        "limite": limite,
                    }
                )
                continue
            rec.activity_schedule(
                activity_type_id=tipo.id,
                date_deadline=termino + relativedelta(days=PRAZO_DEMISSIONAL_DIAS),
                summary=_("Realizar o exame demissional (NR-7, item 7.5.11)"),
                user_id=rec.hr_responsible_id.id or self.env.uid,
            )
            rec.l10n_br_sst_demissional = "cobrado"

    def _l10n_br_sst_demissional_concluido(self):
        """Fecha a cobrança quando o demissional é concluído."""
        tipo = self.env.ref("l10n_br_hr_sst_aso.mail_activity_type_aso_demissional")
        for rec in self:
            rec.activity_ids.filtered(
                lambda a: a.activity_type_id == tipo
            ).action_done()
            rec.l10n_br_sst_demissional = "realizado"
