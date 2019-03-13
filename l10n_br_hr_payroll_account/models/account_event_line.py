# -*- coding: utf-8 -*-
# Copyright 2018 ABGF
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountEventLine(models.Model):
    _inherit = 'account.event.line'

    hr_payslip_line_id = fields.One2many(
        string=u'Linha do Holerite',
        inverse_name='account_event_line_id',
        comodel_name='hr.payslip.line',
    )
