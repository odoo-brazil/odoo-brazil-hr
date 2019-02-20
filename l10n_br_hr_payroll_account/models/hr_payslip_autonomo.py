# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from __future__ import absolute_import, print_function, unicode_literals

import time

from openerp import api, models, fields, _
from openerp.exceptions import Warning

NOME_LANCAMENTO = {
    'normal': u'Holerite Normal - ',
    'rescisao': u'Rescisão - ',
    'ferias': u'Férias - ',
    'decimo_terceiro': u'Décimo Terceiro - ',
    'aviso_previo': u'Aviso Prévio - ',
    'provisao_ferias': u'Provisão de Férias - ',
    'provisao_decimo_terceiro': u'Provisão de Décimo Terceiro - ',
}


class L10nBrHrPayslipAutonomo(models.Model):
    _inherit = b'hr.payslip.autonomo'

    move_id = fields.One2many(
        string='Accounting Entry',
        comodel_name='account.move',
        inverse_name='payslip_autonomo_id',
    )

    move_lines_id = fields.One2many(
        string=u'Lançamentos',
        comodel_name='account.move.line',
        inverse_name='payslip_autonomo_id',
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string=u"Diário",
    )

    @api.multi
    def _buscar_contas(self, salary_rule):
        return False, False
        if self.tipo_de_folha == "provisao_ferias":
            return salary_rule.provisao_ferias_account_debit, salary_rule.\
                provisao_ferias_account_credit
        elif self.tipo_de_folha == "provisao_decimo_terceiro":
            return salary_rule.provisao_13_account_debit, salary_rule.\
                provisao_13_account_credit
        elif self.tipo_de_folha == "normal":
            return salary_rule.holerite_normal_account_debit, salary_rule.\
                holerite_normal_account_credit
        else:
            return False, False

    @api.multi
    def processar_contabilizacao_payslip(self):
        for holerite in self:
            move_obj = self.env['account.move']
            period_obj = self.env['account.period']
            timenow = time.strftime('%Y-%m-%d')
            period_id = period_obj.find(holerite.date_to)
            contador_lancamentos = 1

            if not holerite.journal_id:
                raise Warning(
                    _('Erro de Dados!'),
                    _('O campo Diário neste holerite não foi definido, '
                      'por favor escolha o Diário antes de calcular o '
                      'Lançamento Contábil!')
                )

            # Exclui os Lançamento Contábeis anteriors
            holerite.move_id.unlink()

            # Roda as Rubricas e Cria os lançamentos contábeis
            for line in holerite.line_ids:
                linhas = []
                if line.total > 0:
                    conta_credito, conta_debito = False, False
                    credito, debito = 0, 0
                    if holerite.tipo_de_folha == 'normal':
                        if line.salary_rule_id.holerite_normal_account_debit:
                            debito = line.total
                            conta_debito = \
                                line.salary_rule_id.\
                                    holerite_normal_account_debit
                        if line.salary_rule_id.holerite_normal_account_credit:
                            credito = line.total
                            conta_credito = \
                                line.salary_rule_id.\
                                    holerite_normal_account_credit


                    #
                    # Cria o Lançamento Contábil para esta Rubrica
                    #
                    if conta_credito or conta_debito:
                        move = self.criar_lancamento_contabil(
                                period_id, holerite, contador_lancamentos
                            )

                        # Cria a linha do lançamento contábil para Crédito
                        if conta_credito:
                            credit_line = (0, 0, {
                                'name': line.name,
                                'date': timenow,
                                'account_id': conta_credito.id,
                                'journal_id': holerite.journal_id.id,
                                'period_id': period_id.id,
                                'debit': 0,
                                'credit': credito,
                                'payslip_autonomo_id': holerite.id,
                            })
                            linhas.append(credit_line)

                        # Cria a linha do lançamento contábil para Débito
                        if conta_debito:
                            debit_line = (0, 0, {
                                'name': line.name,
                                'date': timenow,
                                'account_id': conta_debito.id,
                                'journal_id': holerite.journal_id.id,
                                'period_id': period_id.id,
                                'debit': debito,
                                'credit': 0,
                                'payslip_autonomo_id': holerite.id,
                            })
                            linhas.append(debit_line)

                        # Fecha e Posta o Lançamento Contábil
                        move.update({'line_id': linhas})
                        move_id = move_obj.create(move)
                        if holerite.journal_id.entry_posted:
                            move_obj.post(move_id)

                        # Incrementa o contador para a próxima linha
                        contador_lancamentos += 1

    def criar_lancamento_contabil(self, period_id, slip, contador_lancamento):
        name = \
            NOME_LANCAMENTO[slip.tipo_de_folha] \
            + str(slip.mes_do_ano) + "/" + str(slip.ano) \
            + " - " + slip.contract_id.nome_contrato + " - " + \
            str("%03d" % contador_lancamento)
        move = {
            'name': name,
            'display_name': name,
            'narration': name,
            'date': slip.date_from,
            'ref': slip.number,
            'journal_id': slip.journal_id.id,
            'period_id': period_id.id,
            'payslip_autonomo_id': slip.id,
        }
        return move
