# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Classe base com fixtures para testes de férias e 13º salário.
"""
from odoo.addons.l10n_br_hr_payroll.tests.common import PayrollCommon


class VacationCommon(PayrollCommon):
    """Classe base para testes do módulo l10n_br_hr_vacation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.structure_ferias = cls.env.ref("l10n_br_hr_vacation.structure_ferias")
        cls.structure_13_primeira = cls.env.ref(
            "l10n_br_hr_vacation.structure_13_primeira_parcela"
        )
        cls.structure_13_segunda = cls.env.ref(
            "l10n_br_hr_vacation.structure_13_segunda_parcela"
        )
        cls.structure_13 = cls.env.ref("l10n_br_hr_vacation.structure_13")
        cls.structure_rescisao = cls.env.ref("l10n_br_hr_vacation.structure_rescisao")
        cls.leave_type_ferias = cls.env.ref("l10n_br_hr_vacation.leave_type_ferias")
        # Com l10n_br_hr_payroll_account instalado, confirmar o holerite gera
        # lançamento no diário FOPAG. Numa base sem plano de contas (o Odoo 20
        # não carrega plano sem demo) o diário fica sem conta padrão e a
        # confirmação falharia por um motivo alheio a estes testes.
        journal = cls.env.ref(
            "l10n_br_hr_payroll_account.journal_folha_pagamento",
            raise_if_not_found=False,
        )
        if journal and not journal.default_account_id:
            journal.default_account_id = cls.env["account.account"].create(
                {
                    "name": "Salários a Pagar (teste)",
                    "code": "TESTFOPAG",
                    "account_type": "liability_current",
                }
            )
