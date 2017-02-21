# -*- coding: utf-8 -*-
# Copyright 2017 Sei lá
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'L10n Br Hr Falta Abonada',
    'summary': """
        5 faltas abonadas todo ano""",
    'version': '8.0',
    'license': 'AGPL-3',
    'author': 'Sei lá,Odoo Community Association (OCA)',
    'website': 'www.yourcompany.com',
    'depends': [
        'l10n_br_hr_holiday',
        'l10n_br_resource',
        'l10n_br_hr_contract',
        'hr_payroll',
    ],
    'data': [
        'data/hr_holidays_status_data.xml',
    ],
    'demo': [
    ],
}
