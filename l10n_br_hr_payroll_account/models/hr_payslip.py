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

    account_event_template_id = fields.Many2one(
        string='Roteiro Contábil',
        comodel_name='account.event.template'
    )

    move_id = fields.One2many(
        string='Accounting Entry',
        comodel_name='account.move',
        inverse_name='payslip_id',
    )

    move_lines_id = fields.One2many(
        string=u'Lançamentos',
        comodel_name='account.move.line',
        inverse_name='payslip_id',
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string=u"Diário",
        default=lambda self: self._buscar_diario_fopag(),
    )

    @api.multi
    def get_payslip_lines(self, payslip_id):
        """
        docstring
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

            payslip_line.update(codigo_contabil=codigo_contabil)

        return result

    @api.multi
    def _buscar_diario_fopag(self):
        if self.env.context.get('params'):
            return self.env.ref(
                "l10n_br_hr_payroll_account.payroll_account_journal").id
        return self.env["account.journal"]

    def gerar_contabilizacao_rubricas(self):
        """
        Gerar um dict contendo a contabilização de cada rubrica
        return { string 'CODE' : float valor}
        """

        """
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
            if line.salary_rule_id.gerar_contabilizacao:
                contabilizacao_rubricas.append({
                    'code': line.salary_rule_id.code,
                    'valor': line.total,
                    # opcional para historico padrao
                    'name': line.salary_rule_id.name,
                })

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

            if not holerite.account_event_template_id:
                raise Warning(
                    _('Erro de Dados!'),
                    _('O campo Roteiro Contábil neste holerite não foi '
                      'definido, por favor escolha o Diário antes de calcular '
                      'o Lançamento Contábil!'))

            # Exclui os Lançamento Contábeis anteriors
            holerite.move_id.unlink()

            rubricas_para_contabilizar = self.gerar_contabilizacao_rubricas()

            contabilizar = {
                'ref': '{} {}'.format(
                    NOME_LANCAMENTO.get(holerite.tipo_de_folha),
                    holerite.data_mes_ano),
                'data': holerite.date_from,
                'lines': rubricas_para_contabilizar,
            }

            account_move_ids = \
                holerite.account_event_template_id.\
                    gerar_contabilizacao(contabilizar)

            # Criar os relacionamentos
            for account_move_id in account_move_ids:
                account_move_id.payslip_id = holerite.id

            for line_id in account_move_ids.mapped('line_id'):
                line_id.payslip_id = holerite.id
