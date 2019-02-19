# -*- coding: utf-8 -*-
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import (division, print_function, unicode_literals)

from openerp import fields, models


class HrContractSalaryRule(models.Model):

    _inherit = b'hr.contract.salary.rule'

    codigo_contabil = fields.Char(
        string='Código de Contabilização',
    )
