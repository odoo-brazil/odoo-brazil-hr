# -*- coding: utf-8 -*-
# Copyright 2019 ABGF
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    sufixo_code_account = fields.Char(
        string='Sufixo para Contabilização',
        help='Sufixo para código de contabilização. No processamento do '
             'holerite utilizar esse sufixo para compor o '
             'código de contabilização das rúbricas',
    )
