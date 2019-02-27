# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from openerp import api, models, fields, exceptions

NOME_LANCAMENTO_LOTE = {
    'provisao_ferias': u'Provisão de Férias em Lote',
    'adiantamento_13': u'Décimo Terceiro Salário em Lote',
    'decimo_terceiro': u'Décimo Terceiro Salário em Lote',
    'provisao_decimo_terceiro': u'Provisão de 13 em Lote',
    'normal': u'Folha normal em Lote',
}


class L10nBrHrPayslip(models.Model):
    _inherit = b'hr.payslip.run'

    account_event_id = fields.Many2one(
        string='Evento Contábil',
        comodel_name='account.event'
    )

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
