# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class L10nBrHrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    provisao_ferias_account_debit = fields.Many2one(
        comodel_name='account.account',
        string='Conta débito provisão de Férias',
    )
    provisao_ferias_account_credit = fields.Many2one(
        comodel_name='account.account',
        string='Conta crédito provisão de Férias',
    )

    provisao_13_account_debit = fields.Many2one(
        comodel_name='account.account',
        string='Conta débito provisão Décimo 13º',
    )
    provisao_13_account_credit = fields.Many2one(
        comodel_name='account.account',
        string='Conta crédito provisão Décimo 13º',
    )
