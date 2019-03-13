# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import absolute_import, print_function, unicode_literals

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


class L10nBrHrPayslip(models.Model):
    _inherit = b'hr.payslip'

    account_event_id = fields.Many2one(
        string='Evento Contábil',
        comodel_name='account.event'
    )

    @api.multi
    def get_payslip_lines(self, payslip_id):
        """
        """
        # Holerite que esta sendo processado
        holerite_id = self.browse(payslip_id)
        contract_id = holerite_id.contract_id
        salary_rule_obj = self.env['hr.salary.rule']
        rubricas_especificas = \
            holerite_id.get_contract_specific_rubrics(contract_id, [])

        # rubricas processadas pelo holerite
        result = super(L10nBrHrPayslip, self).get_payslip_lines(payslip_id)

        # Para cada rubrica buscar o codigo contabil
        for payslip_line in result:

            rule_id = payslip_line.get('salary_rule_id')
            hr_salary_rule_id = salary_rule_obj.browse(rule_id)
            codigo_contabil = ''

            # Se nao gerar contabilizacao pula a rubrica
            if not hr_salary_rule_id.gerar_contabilizacao:
                continue

            if rule_id in rubricas_especificas:
                # verificar codigo contabil definido na rubrica especifica
                codigo_contabil = \
                    rubricas_especificas.get(rule_id)[0].codigo_contabil

            # buscar diretamente na configuracao da rubrica
            if not codigo_contabil:
                codigo_contabil = \
                    salary_rule_obj.browse(rule_id).codigo_contabil

            # Se nao estiver definido na rubrica utilizar o code da rubrica
            if not codigo_contabil:
                codigo_contabil = payslip_line.get('code')

            # Adicionar o sufixo para contabilização definido no contrato
            if contract_id.sufixo_code_account:
                codigo_contabil += contract_id.sufixo_code_account
            payslip_line.update(codigo_contabil=codigo_contabil)

        return result

    def gerar_contabilizacao_rubricas(self):
        """
        Gerar um dict contendo a contabilização de cada rubrica
        return { string 'CODE' : float valor}
        {
            'data':         '2019-01-01',
            'lines':        [{'code': 'LIQUIDO', 'valor': 123,
                                'historico_padrao': {'mes': '01'}},
                             {'code': 'INSS', 'valor': 621.03}
                                'historico_padrao': {'nome': 'Nome do lança'}},
                            ],
            'ref':          identificação do módulo de origem
            'model':        (opcional) model de origem
            'res_id':       (opcional) id do registro de origem
            'period_id'     (opcional) account.period
            'company_id':   (opcional) res.company
        }
        """
        contabilizacao_rubricas = []

        # Roda as Rubricas e Cria os lançamentos contábeis
        for line in self.line_ids:
            if line.total and line.salary_rule_id.gerar_contabilizacao:
                contabilizacao_rubricas.append((0, 0, {
                    'code': line.codigo_contabil,
                    'valor': line.total,
                    # opcional para historico padrao
                    'name': line.salary_rule_id.name,
                    'hr_payslip_line_id': [(4, line.id)],
                }))
        return contabilizacao_rubricas

    @api.multi
    def processar_contabilizacao_folha(self):
        """
        Rotina que ira processar as rubricas do holerite e baseado em um
        roteiro contabil disparar a contabilização das rubricas
        """
        for holerite in self:

            if holerite.payslip_run_id:
                raise Warning(
                    _('Erro de Consistência!'),
                    _('Este Holerite faz parte de um lote '
                      'neste caso a contabilização deve ser feita pelo Lote!'))

            # Exclui os Lançamento Contábeis anteriors
            holerite.account_event_id.unlink()

            rubricas_para_contabilizar = self.gerar_contabilizacao_rubricas()

            account_event = {
                'ref': '{} {} - {}'.format(
                    NOME_LANCAMENTO.get(holerite.tipo_de_folha),
                    holerite.employee_id.name,
                    holerite.data_mes_ano),
                'data': fields.Date.today(),
                'account_event_line_ids': rubricas_para_contabilizar,
                'origem': '{},{}'.format('hr.payslip', holerite.id),
            }

            holerite.account_event_id = \
                self.env['account.event'].create(account_event)
