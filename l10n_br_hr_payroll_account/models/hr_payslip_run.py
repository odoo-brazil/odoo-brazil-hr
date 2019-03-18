# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import absolute_import, print_function, unicode_literals

from openerp import api, models, fields
from openerp.exceptions import Warning

NOME_LANCAMENTO_LOTE = {
    'provisao_ferias': u'Provisão de Férias em Lote',
    'adiantamento_13': u'Décimo Terceiro Salário em Lote',
    'decimo_terceiro': u'Décimo Terceiro Salário em Lote',
    'provisao_decimo_terceiro': u'Provisão de 13 em Lote',
    'normal': u'Folha normal',
}


class L10nBrHrPayslip(models.Model):
    _inherit = b'hr.payslip.run'

    account_event_id = fields.Many2one(
        string='Evento Contábil',
        comodel_name='account.event'
    )

    @api.multi
    def close_payslip_run(self):
        """
        Adicionar geração do evento contábil no fechamento do Lote de holerites

        """
        self.ensure_one()
        super(L10nBrHrPayslip, self).close_payslip_run()
        self.gerar_contabilizacao_lote()

        if self.tipo_de_folha in ['provisao_decimo_terceiro', 'provisao_ferias']:

            hr_payslip_run_id = self.search([
                ('mes_do_ano','=', self.mes_do_ano - 1),
                ('tipo_de_folha','=', self.tipo_de_folha),
            ])

            if hr_payslip_run_id.account_event_id:
                hr_payslip_run_id.account_event_id.button_reverter_lancamentos()

    @api.multi
    def gerar_rubricas_para_lancamentos_contabeis_lote(self):
        """
        Gerar Lançamentos contábeis apartir do lote de holerites
        """
        self.ensure_one()

        # Dict para totalizar todas rubricas de todos holerites
        all_rubricas = {}

        # Adicionar a rescisao na contabilização do lote
        all_payslip_ids = self.slip_ids + self.payslip_rescisao_ids

        for payslip in all_payslip_ids:
            # Rubricas do holerite para contabilizar
            rubricas_holerite = payslip.gerar_contabilizacao_rubricas()

            for rubrica_holerite in rubricas_holerite:
                # EX.: rubrica_holerite = {'code': 'INSS', 'valor': 621.03}
                code = rubrica_holerite[2].get('code')
                valor = rubrica_holerite[2].get('valor')

                if code in all_rubricas:
                    # Somar rubrica do holerite ao dict totalizador
                    valor_total = all_rubricas.get(code)[2].get('valor') + valor
                    all_rubricas.get(code)[2].update(valor=valor_total)
                else:
                    all_rubricas[code] = rubrica_holerite

        return all_rubricas.values()

    @api.multi
    def gerar_contabilizacao_lote(self):
        """
        Processa a contabilização do lote baseado nas rubricas dos holerites
        """
        for lote in self:

            # Exclui o Evento Contábbil
            lote.account_event_id.unlink()

            rubricas = self.gerar_rubricas_para_lancamentos_contabeis_lote()

            contabiliz = {
                'account_event_line_ids': rubricas,
                'data': '{}-{:02}-01'.format(lote.ano, lote.mes_do_ano),
                'ref': 'Lote de {}'.format(
                    NOME_LANCAMENTO_LOTE.get(lote.tipo_de_folha)),
                'origem': '{},{}'.format('hr.payslip.run', lote.id),
            }

            lote.account_event_id = self.env['account.event'].create(contabiliz)

    @api.multi
    def gerar_codigo_contabilizacao(self):
        """
        Se o lote ja tiver sido processado, os códigos contabeis das rubricas
        nao foram processados. Essa função atualiza as linhas dos holerites do
        lote com o código contabil de cada rubrica
        """
        for record in self:
            for holerite_id in record.slip_ids:
                for line_id in holerite_id.line_ids:

                    # Se nao gerar contabilizacao pula a rubrica
                    if not line_id.salary_rule_id.gerar_contabilizacao:
                        continue

                    line_id.codigo_contabil = \
                        line_id.salary_rule_id.codigo_contabil

                    if not line_id.codigo_contabil:
                        line_id.codigo_contabil = \
                            line_id.salary_rule_id.code

                    # Adicionar o sufixo para contabilização no contrato
                    if line_id.slip_id.contract_id.sufixo_code_account:
                        line_id.codigo_contabil += \
                            line_id.slip_id.contract_id.sufixo_code_account

    @api.multi
    def verificar_fgts_holerites(self):
        """
        """
        for record in self:
            invalidos = ''

            for holerite_id in record.slip_ids:

                fgts_total = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'FGTS').total

                fgts_salario = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'FGTS_F_SALARIO').total or 0.0

                fgts_salario_diretor = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'FGTS_D_SALARIO').total or 0.0

                fgts_ferias = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'FGTS_F_FERIAS').total or 0.0

                fgts_decimo = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'FGTS_F_13').total or 0.0

                fgts_somado = fgts_salario + fgts_ferias + fgts_decimo + \
                              fgts_salario_diretor

                if round(fgts_total, 2) != round(fgts_somado, 2):
                    invalidos += holerite_id.contract_id.display_name + '\n'

            if invalidos:
                raise Warning('FGTS inválido para:\n{}'.format(invalidos))

    @api.multi
    def verificar_inss_empresa_holerites(self):
        """
        """
        for record in self:
            invalidos = ''

            for holerite_id in record.slip_ids:

                fgts_total = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'INSS_EMPRESA_TOTAL').total

                fgts_salario = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'INSS_EMPRESA_F_FERIAS').total or 0.0

                fgts_salario_diretor = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'INSS_EMPRESA_F_SALARIO').total or 0.0

                inss_empresa_salario_diretor = holerite_id.line_ids.filtered(
                    lambda x: x.code == 'INSS_EMPRESA_D_SALARIO').total or 0.0

                fgts_somado = \
                    fgts_salario + fgts_salario_diretor + \
                    inss_empresa_salario_diretor

                if round(fgts_total, 2) != round(fgts_somado, 2):
                    invalidos += holerite_id.contract_id.display_name + '\n'

            if invalidos:
                raise Warning('INSS EMPRESA inválido para:\n{}'.format(invalidos))
