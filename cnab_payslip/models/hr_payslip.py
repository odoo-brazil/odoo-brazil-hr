# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    paid_order = fields.Boolean(
        compute='_compute_paid',
        readonly=True,
        store=True,
    )

    @api.multi
    def test_paid(self):
        if not self.payment_line_ids:
            return False
        for line in self.payment_line_ids:
            if not line.state2:
                return False
            if line.state2 != 'paid':
                return False
        return True

    @api.one
    @api.depends('payment_line_ids.bank_line_id.state2')
    def _compute_paid(self):
        self.paid_order = self.test_paid()
