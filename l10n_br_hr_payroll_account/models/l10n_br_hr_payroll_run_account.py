# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time

from openerp import api, models, fields, _
from openerp.tools import float_compare

NOME_LANCAMENTO_LOTE = {
    'provisao_ferias': u'Provisão de Férias em Lote',
    'provisao_decimo_terceiro': u'Provisão de 13 em Lote',
}


class L10nBrHrPayslip(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def _buscar_lancamentos(self):
        for payslip_run in self:
            if payslip_run.id:
                payslip_run.move_lines_id = \
                    self.env['account.move.line'].search(
                        [
                            ('payslip_run_id', '=', payslip_run.id)
                        ]
                    )

    account_debit = fields.Many2one(
        comodel_name='account.account',
        string='Debit Account',
    )
    account_credit = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account',
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
    def _buscar_contas_lotes(self):
        if self.tipo_de_folha in [
            "provisao_ferias", "provisao_decimo_terceiro"
        ]:
            return self.account_debit, self.account_credit
        else:
            return False, False

    @api.multi
    def _verificar_lancamentos_lotes_anteriores(self, tipo_folha, period_id):
        for payslip in self:
            move_id = self.env['account.move'].search(
                [
                    (
                        'name',
                        'like',
                        NOME_LANCAMENTO_LOTE[tipo_folha]
                    ),
                    (
                        'period_id', '!=', period_id
                    )
                ],
                limit=1
            )
            if not move_id:
                return False
            else:
                return move_id

    @api.multi
    def _valor_lancamento_lote_anterior_rubrica(self, move_id, rubrica_name):
        for line in move_id.line_id:
            if rubrica_name == line.name:
                return line.debit, line.credit
        return 0, 0

    @api.multi
    def processar_folha(self):
        conta_debito, conta_credito = self._buscar_contas_lotes()
        if conta_debito or conta_credito:
            for payslip_run in self:
                move_obj = self.env['account.move']
                period_obj = self.env['account.period']
                precision = \
                    self.env['decimal.precision'].precision_get('Payroll')
                timenow = time.strftime('%Y-%m-%d')
                period_id = period_obj.find(payslip_run.date_start)
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                if payslip_run.move_id:
                    move = payslip_run.move_id
                    move_lines = self.env['account.move.line'].search(
                        [
                            ('move_id', '=', move.id)
                        ]
                    )
                    for line in move_lines:
                        line.unlink()
                else:
                    name = NOME_LANCAMENTO_LOTE[payslip_run.tipo_de_folha] \
                           + " - " + str(payslip_run.mes_do_ano) + "/" \
                           + str(payslip_run.ano)
                    move = {
                        'name': name,
                        'display_name': name,
                        'narration': name,
                        'date': payslip_run.date_end,
                        'ref': payslip_run.display_name,
                        'journal_id': payslip_run.journal_id.id,
                        'period_id': period_id.id,
                        'payslip_run_id': payslip_run.id,
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
                move_anterior_id = \
                    self._verificar_lancamentos_lotes_anteriores(
                        payslip_run.tipo_de_folha, period_id.id
                    )
                for rubrica in rubricas:
                    if payslip_run.tipo_de_folha in [
                        'provisao_ferias',
                        'provisao_decimo_terceiro'
                    ]:
                        if move_anterior_id:
                            debito, credito = self\
                                ._valor_lancamento_lote_anterior_rubrica(
                                    move_anterior_id, rubrica
                                )
                            if debito or credito:
                                line_anterior = (0, 0, {
                                    'name': rubrica + " (Anterior)",
                                    'date': timenow,
                                    'account_id': conta_debito.id if debito
                                    else conta_credito.id,
                                    'journal_id': payslip_run.journal_id.id,
                                    'period_id': period_id.id,
                                    'debit': credito or 0.0,
                                    'credit': debito or 0.0,
                                    'payslip_run_id': payslip_run.id,
                                })
                                line_ids.append(line_anterior)
                                if debito:
                                    debit_sum += \
                                        line_anterior[2]['debit'] - \
                                        line_anterior[2]['credit']
                                else:
                                    credit_sum += \
                                        line_anterior[2]['credit'] - \
                                        line_anterior[2]['debit']
                    if conta_credito:
                        credit_line = (0, 0, {
                            'name': rubrica,
                            'date': timenow,
                            'account_id': conta_credito.id,
                            'journal_id': payslip_run.journal_id.id,
                            'period_id': period_id.id,
                            'debit': 0.0,
                            'credit': rubricas[rubrica],
                            'payslip_run_id': payslip_run.id,
                        })
                        line_ids.append(credit_line)
                        credit_sum += \
                            credit_line[2]['credit'] - credit_line[2]['debit']
                if float_compare(
                        credit_sum, debit_sum, precision_digits=precision
                ) == -1:
                    acc_id = \
                        payslip_run.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise Warning(_('Configuration Error!'),
                                      _('The Expense Journal "%s" has not'
                                        ' properly configured '
                                        'the Credit Account!'
                                        ) % payslip_run.journal_id.name)
                    adjust_credit = (0, 0, {
                        'name': _('Adjustment Entry'),
                        'date': timenow,
                        'partner_id': False,
                        'account_id': conta_credito.id,
                        'journal_id': payslip_run.journal_id.id,
                        'period_id': period_id.id,
                        'debit': 0.0,
                        'credit': debit_sum - credit_sum,
                        'payslip_run_id': payslip_run.id,
                    })
                    line_ids.append(adjust_credit)

                elif float_compare(
                        debit_sum, credit_sum, precision_digits=precision
                ) == -1:
                    acc_id = payslip_run.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise Warning(_('Configuration Error!'),
                                      _('The Expense Journal "%s" has not'
                                        ' properly configured '
                                        'the Debit Account!'
                                        ) % payslip_run.journal_id.name)
                    adjust_debit = (0, 0, {
                        'name': _('Adjustment Entry'),
                        'date': timenow,
                        'partner_id': False,
                        'account_id': conta_debito.id,
                        'journal_id': payslip_run.journal_id.id,
                        'period_id': period_id.id,
                        'debit': credit_sum - debit_sum,
                        'credit': 0.0,
                        'payslip_run_id': payslip_run.id
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
