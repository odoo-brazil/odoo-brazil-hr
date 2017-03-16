# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time

from openerp import api, models, fields, _
from openerp.tools import float_compare, float_is_zero

NOME_LANCAMENTO = {
    'provisao_ferias': u'Provisão de Férias - ',
}


class L10nBrHrPayslip(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def _buscar_lancamentos(self):
        for payslip in self:
            if payslip.id:
                payslip.move_lines_id = self.env['account.move.line'].search(
                    [
                        ('payslip_id', '=', payslip.id)
                    ]
                )

    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Accounting Entry',
    )

    move_lines_id = fields.One2many(
        comodel_name='account.move.line',
        string=u'Lançamentos',
        compute=_buscar_lancamentos
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string=u"Diário",
        required=True,
    )

    @api.multi
    def gerar_holerites(self):
        super(L10nBrHrPayslip, self).gerar_holerites()
        for payslip_run in self:
            move_obj = self.env['account.move']
            period_obj = self.env['account.period']
            precision = self.env['decimal.precision'].precision_get('Payroll')
            timenow = time.strftime('%Y-%m-%d')
            period_id = period_obj.find(payslip_run.date_start)
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            name = u'Lote Provisão Férias' + " - " + \
                   str(payslip_run.mes_do_ano) + "/" + str(payslip_run.ano)
            move = {
                'name': name,
                'display_name': name,
                'narration': name,
                'date': payslip_run.date_end,
                'ref': payslip_run.display_name,
                'journal_id': payslip_run.journal_id.id,
                'period_id': period_id.id,
                'payslip_id': payslip_run.id,
            }
            rubricas = {}
            for payslip in self.slip_ids:
                for line in payslip.details_by_salary_rule_category:
                    if line.salary_rule_id.account_debit.id \
                            or line.salary_rule_id.account_credit.id:
                        if not rubricas.get(line.name):
                            rubricas.update({line.name: line.total})
                        else:
                            rubricas[line.name] += line.total
            for rubrica in rubricas:
                if self.credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'date': timenow,
                        'account_id': self.credit_account_id,
                        'journal_id': payslip_run.journal_id.id,
                        'period_id': period_id.id,
                        'debit': 0.0,
                        'credit': rubrica,
                    })
                    line_ids.append(credit_line)
                    credit_sum += \
                        credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(
                    credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = payslip_run.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise Warning(_('Configuration Error!'),
                                  _('The Expense Journal "%s" has not properly'
                                    ' configured the Credit Account!'
                                    ) % payslip_run.journal_id.name)
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': payslip_run.journal_id.id,
                    'period_id': period_id.id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                    'payslip_id': payslip_run.id,
                })
                line_ids.append(adjust_credit)

            elif float_compare(
                    debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = payslip_run.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise Warning(_('Configuration Error!'),
                                  _('The Expense Journal "%s" has not properly'
                                    ' configured the Debit Account!'
                                    ) % payslip_run.journal_id.name)
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': payslip_run.journal_id.id,
                    'period_id': period_id.id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            if not payslip_run.move_id:
                move.update({'line_id': line_ids})
                move_id = move_obj.create(move)
            else:
                for line in line_ids:
                    line[2].update({'move_id': payslip_run.move_id.id})
                    self.env['account.move.line'].create(line[2])
                move_id = payslip_run.move_id
            self.write({'move_id': move_id.id})
            if payslip_run.journal_id.entry_posted:
                move_obj.post(move_id)
