# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class L10nBrHrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    account_debit = fields.Many2one(
        comodel_name='account.account',
        string='Debit Account',
    )
    account_credit = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account',
    )
