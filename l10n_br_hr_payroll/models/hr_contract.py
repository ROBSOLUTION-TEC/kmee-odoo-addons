# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .res_company import SIMPLES_ANEXO


class HrContract(models.Model):
    # Odoo 19+: hr.contract was merged into hr.version (employee versions)
    _inherit = "hr.version"

    l10n_br_hr_simples_anexo = fields.Selection(
        selection=SIMPLES_ANEXO,
        string="Anexo do Simples (Atividade)",
        help="Anexo do Simples Nacional da atividade exercida pelo empregado, "
        "quando diferente do anexo preponderante da empresa. Vazio = usa o "
        "anexo da empresa.\n\n"
        "Serve à atividade concomitante do Simples: uma optante com atividade "
        "do anexo IV (construção civil, vigilância, limpeza) recolhe a "
        "contribuição patronal por fora do DAS (LC 123/2006, art. 18, §5º-C) "
        "para os empregados dessa atividade, ainda que o anexo preponderante "
        "seja outro. É eixo INDEPENDENTE da desoneração/CPRB.",
    )
    l10n_br_periculosidade = fields.Boolean(
        string="Periculosidade",
        help="Adicional de periculosidade (30% do salário base)",
    )
    l10n_br_insalubridade = fields.Boolean(
        string="Insalubridade",
    )
    l10n_br_grau_insalubridade = fields.Selection(
        selection=[
            ("minimo", "Mínimo (10%)"),
            ("medio", "Médio (20%)"),
            ("maximo", "Máximo (40%)"),
        ],
        string="Grau de Insalubridade",
    )

    # Divisor mensal padrão CLT (44h semanais × 5): usado como fallback
    # quando o contrato não tem calendário de trabalho configurado.
    _L10N_BR_DIVISOR_PADRAO = 220.0

    def _l10n_br_horas_semanais(self):
        """Horas contratuais semanais derivadas do calendário de trabalho.

        Odoo 20: o calendário já calcula a média semanal
        (``hours_per_week``, a partir de ``duration_hours`` das presenças de
        trabalho); calendários variáveis/indefinidos guardam o valor
        informado pelo usuário no mesmo campo.

        Returns:
            Horas semanais (float); ``0.0`` se não houver calendário/jornada.
        """
        self.ensure_one()
        calendar = self.resource_calendar_id
        if not calendar:
            return 0.0
        return calendar.hours_per_week or 0.0

    def _l10n_br_divisor_horas_mensais(self):
        """Divisor mensal de horas para cálculo do salário-hora (RF-26).

        Deriva da jornada do contrato: ``horas_semanais × 5`` (equivale a
        ``horas_semanais / 6 × 30`` da CLT — 44h → 220, 40h → 200). Quando o
        contrato não tem calendário/jornada, usa o divisor padrão de 220.
        """
        self.ensure_one()
        horas_semanais = self._l10n_br_horas_semanais()
        if not horas_semanais:
            return self._L10N_BR_DIVISOR_PADRAO
        return horas_semanais * 5.0

    @api.constrains("l10n_br_periculosidade", "l10n_br_insalubridade")
    def _check_periculosidade_insalubridade(self):
        """Periculosidade e insalubridade não acumulam (Súmula 364 TST)."""
        for rec in self:
            if rec.l10n_br_periculosidade and rec.l10n_br_insalubridade:
                raise ValidationError(
                    _(
                        "Não é permitido acumular periculosidade e insalubridade "
                        "(Súmula 364 do TST)."
                    )
                )

    @api.model
    def _get_whitelist_fields_from_template(self):
        whitelist = super()._get_whitelist_fields_from_template()
        for field_name in (
            "l10n_br_hr_simples_anexo",
            "l10n_br_periculosidade",
            "l10n_br_insalubridade",
            "l10n_br_grau_insalubridade",
        ):
            if field_name not in whitelist:
                whitelist.append(field_name)
        return whitelist
