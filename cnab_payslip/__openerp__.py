# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cnab Payslip',
    'description': """
        Junção do módulo do cnab ao módulo de payroll""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'depends': [
        'l10n_br_hr_payment_order',
        'l10n_br_account_banking_payment_cnab',

    ],
    'data': [
        'hr_payroll_workflow.xml',
        'views/hr_payslip.xml',
    ],
    'demo': [
    ],
}
