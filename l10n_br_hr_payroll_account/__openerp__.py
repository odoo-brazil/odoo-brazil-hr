# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Brazilian Localization HR Payroll Account',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'KMEE, ABGF, Odoo Community Association (OCA)',
    'maintainer': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'version': '8.0.0.0.1',
    'depends': [
        'l10n_br_hr_payroll',
        'l10n_br_contabilidade',
    ],
    'data': [
        'data/journal_data.xml',
        'views/hr_payslip.xml',
        'views/hr_payslip_run.xml',
        'views/hr_salary_rule.xml',
        'views/hr_contract.xml',
        # 'views/l10n_br_hr_payroll_autonomo.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
