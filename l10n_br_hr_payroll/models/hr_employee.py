# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Odoo 20: campos do empregado fora do perfil público (hr.employee.public)
    # precisam de grupo de RH; são dados pessoais/sensíveis (LGPD).

    l10n_br_tipo_contrato = fields.Selection(
        groups="hr.group_hr_user",
        selection=[
            ("clt", "CLT"),
            ("estatutario", "Estatutário"),
            ("aprendiz", "Aprendiz"),
            ("temporario", "Temporário"),
        ],
        string="Tipo de Contrato",
        default="clt",
    )
    l10n_br_irrf_dependentes = fields.Integer(
        groups="hr.group_hr_user",
        string="Dependentes IRRF",
        default=0,
    )
    l10n_br_pensao_alimenticia = fields.Float(
        groups="hr.group_hr_user",
        string="Pensão Alimentícia (Valor Fixo)",
        default=0.0,
        help="Parcela fixa mensal de pensão alimentícia determinada "
        "judicialmente. Somada à parcela percentual (se houver).",
    )
    l10n_br_pensao_percentual = fields.Float(
        groups="hr.group_hr_user",
        string="Pensão Alimentícia (% da Remuneração)",
        default=0.0,
        help="Percentual da remuneração bruta destinado à pensão alimentícia "
        "(ex.: 30 = 30%). O valor efetivo descontado é: valor fixo + "
        "percentual sobre a remuneração bruta do mês.",
    )
    l10n_br_molestia_grave = fields.Boolean(
        groups="hr.group_hr_user",
        string="Portador de Moléstia Grave",
        help="Isenção de IRRF conforme Lei 7.713/88",
    )
    l10n_br_cid_molestia = fields.Char(
        groups="hr.group_hr_user",
        string="CID da Moléstia",
    )
    l10n_br_pcd = fields.Boolean(
        groups="hr.group_hr_user",
        string="Pessoa com Deficiência",
    )
    l10n_br_num_filhos_sf = fields.Integer(
        groups="hr.group_hr_user",
        string="Filhos para Salário Família",
        help="Filhos até 14 anos ou inválidos de qualquer idade",
        default=0,
    )
    l10n_br_filhos_invalidos_sf = fields.Integer(
        groups="hr.group_hr_user",
        string="Filhos Inválidos (Salário Família)",
        help="Filhos inválidos de qualquer idade que recebem salário família",
        default=0,
    )
