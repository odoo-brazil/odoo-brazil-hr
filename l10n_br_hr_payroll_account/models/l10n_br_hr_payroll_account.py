# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time

from openerp import api, models, fields, _
from openerp.tools import float_compare, float_is_zero
from openerp.exceptions import Warning

NOME_LANCAMENTO = {
    'provisao_ferias': u'Provisão de Férias - ',
}


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


class L10nBrHrPayslip(models.Model):
    _inherit = 'hr.payslip'

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
    def processar_folha(self):
        move_obj = self.env['account.move']
        period_obj = self.env['account.period']
        precision = self.env['decimal.precision'].precision_get('Payroll')
        timenow = time.strftime('%Y-%m-%d')

        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            period_id = period_obj.find(slip.date_to)
            default_partner_id = slip.employee_id.address_home_id.id
            if slip.move_id:
                move = slip.move_id
                move_lines = self.env['account.move.line'].search(
                    [
                        ('move_id', '=', move.id)
                    ]
                )
                for line in move_lines:
                    line.unlink()
            else:
                name = \
                    NOME_LANCAMENTO[slip.tipo_de_folha] \
                    + str(slip.mes_do_ano) + "/" + str(slip.ano) \
                    + " - " + slip.contract_id.nome_contrato
                move = {
                    'name': name,
                    'display_name': name,
                    'narration': name,
                    'date': slip.date_from,
                    'ref': slip.number,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id.id,
                    'payslip_id': slip.id,
                }
            for line in slip.details_by_salary_rule_category:
                if line.salary_rule_id.account_debit.id \
                        or line.salary_rule_id.account_credit.id:
                    amt = slip.credit_note and -line.total or line.total
                    if float_is_zero(amt, precision_digits=precision):
                        continue
                    partner_id = \
                        line.salary_rule_id.register_id.partner_id \
                        and line.salary_rule_id.register_id.partner_id.id \
                        or default_partner_id
                    debit_account_id = line.salary_rule_id.account_debit.id
                    credit_account_id = line.salary_rule_id.account_credit.id

                    if debit_account_id:
                        debit_line = (0, 0, {
                            'name': line.name,
                            'date': timenow,
                            'partner_id':
                                (
                                    line.salary_rule_id.register_id.
                                    partner_id or line.salary_rule_id.
                                    account_debit.type in (
                                        'receivable', 'payable'
                                    )
                                ) and partner_id or False,
                            'account_id': debit_account_id,
                            'journal_id': slip.journal_id.id,
                            'period_id': period_id.id,
                            'debit': amt > 0.0 and amt or 0.0,
                            'credit': amt < 0.0 and -amt or 0.0,
                            'payslip_id': slip.id,
                        })
                        line_ids.append(debit_line)
                        debit_sum += \
                            debit_line[2]['debit'] - debit_line[2]['credit']

                    if credit_account_id:
                        credit_line = (0, 0, {
                            'name': line.name,
                            'date': timenow,
                            'partner_id':
                                (
                                    line.salary_rule_id.register_id.
                                    partner_id or line.salary_rule_id.
                                    account_credit.type in (
                                        'receivable', 'payable'
                                    )
                                ) and partner_id or False,
                            'account_id': credit_account_id,
                            'journal_id': slip.journal_id.id,
                            'period_id': period_id.id,
                            'debit': amt < 0.0 and -amt or 0.0,
                            'credit': amt > 0.0 and amt or 0.0,
                            'payslip_id': slip.id,
                        })
                        line_ids.append(credit_line)
                        credit_sum += \
                            credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(
                    credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise Warning(_('Configuration Error!'),
                                  _('The Expense Journal "%s" has not properly'
                                    ' configured the Credit Account!'
                                    ) % slip.journal_id.name)
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id.id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                    'payslip_id': slip.id,
                })
                line_ids.append(adjust_credit)

            elif float_compare(
                    debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise Warning(_('Configuration Error!'),
                                  _('The Expense Journal "%s" has not properly'
                                    ' configured the Debit Account!'
                                    ) % slip.journal_id.name)
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id.id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                    'payslip_id': slip.id,
                })
                line_ids.append(adjust_debit)
            if not slip.move_id:
                move.update({'line_id': line_ids})
                move_id = move_obj.create(move)
            else:
                for line in line_ids:
                    line[2].update({'move_id': slip.move_id.id})
                    self.env['account.move.line'].create(line[2])
                move_id = slip.move_id
            self.write({'move_id': move_id.id})
            if slip.journal_id.entry_posted:
                move_obj.post(move_id)
