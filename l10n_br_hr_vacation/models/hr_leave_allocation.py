# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.l10n_br_hr_payroll.models.salary_rules_br import calc_ferias_dias


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    l10n_br_faltas_periodo_aquisitivo = fields.Integer(
        string="Faltas no Período Aquisitivo",
        default=0,
        help="Faltas injustificadas no período aquisitivo (CLT art. 130)",
    )

    def _l10n_br_aplicar_dias_ferias(self):
        """Dias de direito das alocações de férias (CLT art. 130).

        Odoo 20: ``number_of_days`` deixou de ser computado no hr_holidays
        (é um campo simples com ``default=1``), então os dias de direito são
        aplicados explicitamente na criação e quando as faltas do período
        aquisitivo (ou o tipo da alocação) mudam.
        """
        vacation_type = self.env.ref(
            "l10n_br_hr_vacation.leave_type_ferias", raise_if_not_found=False
        )
        if not vacation_type:
            return
        for alloc in self.filtered(lambda a: a.work_entry_type_id == vacation_type):
            dias = calc_ferias_dias(alloc.l10n_br_faltas_periodo_aquisitivo)
            # number_of_days > 0 is required for regular allocations. When the
            # employee loses the vacation right (33+ faltas), we keep 1 day
            # to satisfy the constraint; the faltas field signals the loss.
            dias = max(dias, 1) if dias == 0 else dias
            if alloc.number_of_days != dias:
                alloc.number_of_days = dias

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._l10n_br_aplicar_dias_ferias()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"l10n_br_faltas_periodo_aquisitivo", "work_entry_type_id"} & set(vals):
            self._l10n_br_aplicar_dias_ferias()
        return res
