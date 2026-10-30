
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/KMEE/kmee-odoo-addons/actions/workflows/pre-commit.yml/badge.svg?branch=20.0)](https://github.com/KMEE/kmee-odoo-addons/actions/workflows/pre-commit.yml?query=branch%3A20.0)
[![Build Status](https://github.com/KMEE/kmee-odoo-addons/actions/workflows/test.yml/badge.svg?branch=20.0)](https://github.com/KMEE/kmee-odoo-addons/actions/workflows/test.yml?query=branch%3A20.0)
[![codecov](https://codecov.io/gh/KMEE/kmee-odoo-addons/branch/20.0/graph/badge.svg)](https://codecov.io/gh/KMEE/kmee-odoo-addons)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# KMEE Odoo Addons

Welcome to our repository, dedicated to incubating OCA modules developed by KMEE. Our goal is to foster innovation and enhance the functionality of Odoo with cutting-edge solutions tailored to meet the diverse needs of businesses. By leveraging our expertise and commitment to quality, we aim to contribute robust and efficient modules that seamlessly integrate into the OCA ecosystem, driving productivity and growth for users worldwide.

Available addons (Odoo360 20.0 branch)
--------------------------------------
This branch of the ROBSOLUTION-TEC fork only carries the Brazilian payroll
modules ported from KMEE 18.0 to Odoo 20.0 (hr.contract -> hr.version,
hr.leave.type -> hr.work.entry.type). They depend on OCA/payroll
(ROBSOLUTION-TEC/oca-payroll, branch 20.0-odoo360), OCA/hr-holidays and OCA/calendar
(ROBSOLUTION-TEC/oca-hr-holidays, oca-calendar) and OCA/l10n-brazil.
l10n_br_esocial needs the Python library esociallib (0.1.3).

Addon | Version | Summary
--- | --- | ---
[l10n_br_hr_payroll](l10n_br_hr_payroll) | 20.0.1.0.0 | Folha de pagamento brasileira com INSS, IRRF, FGTS e verbas CLT
[l10n_br_hr_holiday](l10n_br_hr_holiday) | 20.0.1.0.0 | Tipos de afastamento CLT para a folha de pagamento brasileira
[l10n_br_hr_vacation](l10n_br_hr_vacation) | 20.0.1.0.0 | Férias CLT (art. 130), abono pecuniário e 13º salário
[l10n_br_hr_benefit](l10n_br_hr_benefit) | 20.0.1.0.0 | VT, VR, VA, Plano de Saúde na folha de pagamento BR
[l10n_br_hr_payroll_report](l10n_br_hr_payroll_report) | 20.0.1.0.0 | Holerite, recibo de férias, rescisão e ficha de registro
[l10n_br_hr_payroll_account](l10n_br_hr_payroll_account) | 20.0.1.0.0 | Integração contábil da folha de pagamento BR
[l10n_br_hr_syndicate](l10n_br_hr_syndicate) | 20.0.1.0.0 | Convenções coletivas, piso salarial e contribuição sindical
[l10n_br_hr_validacao_folha](l10n_br_hr_validacao_folha) | 20.0.1.0.0 | Validações e consistências da folha de pagamento BR
[l10n_br_hr_substituicao](l10n_br_hr_substituicao) | 20.0.1.0.0 | Registro de substituicao temporaria de funcionarios
[l10n_br_esocial](l10n_br_esocial) | 20.0.1.0.0 | Tabelas, eventos e transmissão eSocial S-1.3
[l10n_br_hr_holidays_public](l10n_br_hr_holidays_public) | 20.0.1.0.0 | L10n Br HR Holidays Public
[l10n_br_hr_arquivos_governo](l10n_br_hr_arquivos_governo) | 20.0.1.0.0 | DIRF, SEFIP e CAGED (descontinuado): consulta de histórico apenas
[l10n_br_hr_gerador_holerite](l10n_br_hr_gerador_holerite) | 20.0.1.0.0 | BR Payroll - Gerador de Holerites

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)
[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [LGPL-3.0](LICENSE).

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
