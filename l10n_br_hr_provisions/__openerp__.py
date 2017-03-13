# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Brazilian Localization HR Provisions',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'KMEE, Odoo Community Association (OCA)',
    'maintainer': 'KMEE',
    'website': 'http://www.kmee.com.br',
    'version': '8.0.1.0.0',
    'depends': [
        'l10n_br_hr_payroll',
    ],
    'data': [
        "views/l10n_br_hr_provisions_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}