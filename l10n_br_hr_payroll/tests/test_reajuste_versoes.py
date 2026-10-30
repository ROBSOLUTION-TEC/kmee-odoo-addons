# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Testes: reajuste no meio do mês (Odoo 20, versões do contrato).

No Odoo 19+ uma alteração contratual cria uma nova versão (``hr.version``)
do empregado, com data efetiva própria. Quando duas versões do mesmo
contrato vigoram no período do holerite, o salário é proporcional aos dias
de cada vigência (mês comercial de 30 dias) e os descontos progressivos
(INSS/IRRF) são apurados uma única vez sobre o total do mês.
"""
from datetime import date

from .common import PayrollCommon


class TestReajusteVersoes(PayrollCommon):
    def _reajustar(self, employee, data, salario):
        versao = employee.create_version({"date_version": data, "wage": salario})
        versao.wage = salario
        return versao

    def _linhas(self, payslip, code):
        return payslip.line_ids.filtered(lambda line: line.code == code)

    def test_sem_reajuste_mantem_salario_contratual(self):
        emp = self._create_employee()
        contract = self._create_contract(emp, wage=3000.00)
        payslip = self._create_payslip(emp, contract)
        self.assertAlmostEqualMoney(self._get_line_total(payslip, "SALARIO_BASE"), 3000)

    def test_reajuste_no_dia_16_metade_de_cada_salario(self):
        """Reajuste em 16/03: 15 dias a R$ 3.000 e 15 dias a R$ 4.000."""
        emp = self._create_employee()
        antiga = self._create_contract(emp, wage=3000.00)
        nova = self._reajustar(emp, date(2024, 3, 16), 4000.00)
        self.assertEqual(nova.contract_date_start, antiga.contract_date_start)
        self.assertNotEqual(nova, antiga)
        payslip = self._create_payslip(emp, antiga)
        self.assertAlmostEqualMoney(self._get_line_total(payslip, "SALARIO_BASE"), 3500)
        vigencias = payslip._l10n_br_vigencias_salario(nova)
        self.assertEqual([(v, d) for v, d in vigencias], [(antiga, 15), (nova, 15)])

    def test_regras_calculadas_uma_vez(self):
        """INSS e IRRF apurados uma única vez, sobre o salário do mês."""
        emp = self._create_employee()
        antiga = self._create_contract(emp, wage=3000.00)
        nova = self._reajustar(emp, date(2024, 3, 16), 4000.00)
        payslip = self._create_payslip(emp, antiga)
        self.assertEqual(payslip._get_employee_contracts(), nova)
        self.assertEqual(len(self._linhas(payslip, "SALARIO_BASE")), 1)
        self.assertEqual(len(self._linhas(payslip, "INSS")), 1)
        # INSS sobre R$ 3.500 (base proporcional), não sobre 3.000 + 4.000
        emp_ref = self._create_employee(name="Referência")
        ref = self._create_payslip(emp_ref, self._create_contract(emp_ref, wage=3500.00))
        self.assertAlmostEqualMoney(
            abs(self._get_line_total(payslip, "INSS")),
            abs(self._get_line_total(ref, "INSS")),
        )

    def test_dias_trabalhados_desde_o_inicio_do_periodo(self):
        """WORK100 conta o mês inteiro, não só desde o reajuste."""
        emp = self._create_employee()
        antiga = self._create_contract(emp, wage=3000.00)
        self._reajustar(emp, date(2024, 3, 16), 4000.00)
        payslip = self._create_payslip(emp, antiga)
        emp_ref = self._create_employee(name="Sem reajuste")
        ref = self._create_payslip(emp_ref, self._create_contract(emp_ref, wage=3000.00))
        work = payslip.worked_days_line_ids.filtered(lambda w: w.code == "WORK100")
        work_ref = ref.worked_days_line_ids.filtered(lambda w: w.code == "WORK100")
        self.assertEqual(len(work), 1)
        self.assertEqual(work.number_of_days, work_ref.number_of_days)

    def test_admissao_e_reajuste_no_mesmo_mes(self):
        """Admissão em 01/03 e reajuste em 11/03: 10 dias + 20 dias."""
        emp = self._create_employee()
        antiga = self._create_contract(emp, wage=3000.00, date_start=date(2024, 3, 1))
        self._reajustar(emp, date(2024, 3, 11), 4500.00)
        payslip = self._create_payslip(emp, antiga)
        esperado = 3000 * 10 / 30 + 4500 * 20 / 30
        self.assertAlmostEqualMoney(
            self._get_line_total(payslip, "SALARIO_BASE"), esperado
        )

    def test_reajuste_fora_do_periodo_nao_altera(self):
        """Reajuste em abril não afeta o holerite de março."""
        emp = self._create_employee()
        antiga = self._create_contract(emp, wage=3000.00)
        self._reajustar(emp, date(2024, 4, 1), 4000.00)
        payslip = self._create_payslip(emp, antiga)
        self.assertAlmostEqualMoney(self._get_line_total(payslip, "SALARIO_BASE"), 3000)
        abril = self._create_payslip(
            emp, antiga, date_from=date(2024, 4, 1), date_to=date(2024, 4, 30)
        )
        self.assertAlmostEqualMoney(self._get_line_total(abril, "SALARIO_BASE"), 4000)
