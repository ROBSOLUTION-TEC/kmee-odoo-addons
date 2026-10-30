# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Odoo 20: campos do empregado fora do perfil público (hr.employee.public)
    # precisam de grupo de RH; são dados pessoais/sensíveis (LGPD).

    l10n_br_esocial_matricula = fields.Char(
        groups="hr.group_hr_user",
        string="Matrícula eSocial",
        size=30,
        help="Matrícula atribuída ao trabalhador pela empresa.",
    )
    l10n_br_esocial_categoria_id = fields.Many2one(
        "l10n_br.esocial.categoria.trabalhador",
        groups="hr.group_hr_user",
        string="Categoria Trabalhador eSocial",
        help="Categoria do trabalhador conforme Tabela 1 do eSocial.",
    )
