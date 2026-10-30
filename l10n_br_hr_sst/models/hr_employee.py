# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Odoo 20: l10n_br_sst_ambiente_id vem da versão corrente (hr.version)
    # pela delegação (_inherits) do hr.employee.

    def _l10n_br_sst_riscos_vigentes(self, data=None):
        """Riscos vigentes do contrato ativo do empregado."""
        self.ensure_one()
        if not self.version_id:
            return self.env["l10n_br.sst.risco"]
        return self.version_id._l10n_br_sst_riscos_vigentes(data)
