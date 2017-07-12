# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class HrPayslip(models.Model):

    _inherit = 'hr.payslip'

    paid_order = fields.Boolean(
        compute='_compute_paid',
        default=False,
        store=False,
    )

    # confirmar os states
    def test_paid(self):
        if not self.payment_line_ids:
            return False
        for line in self.payment_line_ids:
            print line.status
            if line.status in ('draft', 'done', 'error'):
                return False
        return True

    @api.depends('payment_line_ids')
    def _compute_paid(self):
        self.paid_order = self.test_paid()
