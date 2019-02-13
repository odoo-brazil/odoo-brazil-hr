# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from openerp import api, models, fields, exceptions


class L10nBrHrPayslip(models.Model):
    _inherit = b'hr.payslip.run'

    account_event_template_id = fields.Many2one(
        string='Roteiro Contábil',
        comodel_name='account.event.template'
    )

    move_id = fields.One2many(
        string='Movimentações Contábeis',
        comodel_name='account.move',
        inverse_name='payslip_run_id',
    )

    move_lines_ids = fields.One2many(
        string=u'Lançamentos',
        comodel_name='account.move.line',
        inverse_name='payslip_run_id',
    )

    @api.multi
    def _verificar_lancamentos_lotes_anteriores(self, tipo_folha, period_id):
        """

        :param tipo_folha:
        :param period_id:
        :return:
        """
        period_obj = self.env['account.period']

        for payslip in self:

            # Calcular o mês/ano anterior
            mes_anterior = payslip.mes_do_ano - 1
            ano_anterior = payslip.ano
            if mes_anterior == 0:
                mes_anterior = 12
                ano_anterior -= 1

            primeiro_dia_do_mes = str(
                datetime.strptime(str(mes_anterior) + '-' +
                                  str(ano_anterior), '%m-%Y'))

            # Encontrar o Período anterior
            periodo_anterior_id = period_obj.find(primeiro_dia_do_mes)

            # Encontrar o Lote anterior
            lote_anterior = self.env['hr.payslip.run'].search(
                [
                    ('mes_do_ano', '=', mes_anterior),
                    ('ano', '=', ano_anterior),
                    ('company_id', '=', payslip.company_id.id),
                    ('tipo_de_folha', '=', payslip.tipo_de_folha)
                ]
            )

            if lote_anterior:
                move_ids = self.env['account.move'].search(
                    [
                        ('ref', 'like', lote_anterior.display_name),
                        ('period_id', '=', periodo_anterior_id.id),
                        ('payslip_run_id', '!=', False),
                    ],
                )

                # Se for provisão de 13º e o mês anterior for Dezembro, não deve
                # desfazer os lançamentos anteriores
                #
                if tipo_folha == 'provisao_13' and mes_anterior == 12:
                    return False

                return move_ids
            else:
                return False


    @api.multi
    def gerar_rubricas_para_lancamentos_contabeis_lote(self):
        """
        Gerar Lançamentos contábeis apartir do lote de holerites
        """
        self.ensure_one()

        if not self.account_event_template_id:
            raise exceptions.Warning(
                ("Erro!"),
                ("É preciso selecionar um Roteiro Contábil para realizar "
                 "a contabilização!"))

        all_rubricas = {}

        # Adicionar a rescisao na contabilização do lote
        all_payslip_ids = self.slip_ids + self.payslip_rescisao_ids

        for payslip in all_payslip_ids:

            rubricas_holerite = payslip.gerar_contabilizacao_rubricas

            for linha_rubrica in rubricas_holerite:
                if linha_rubrica in all_rubricas:
                    all_rubricas[linha_rubrica] += \
                        rubricas_holerite[linha_rubrica]
                else:
                    all_rubricas[linha_rubrica] = \
                        rubricas_holerite[linha_rubrica]

        return all_rubricas


    @api.multi
    def gerar_contabilizacao_lote(self):
        """
        Processa a contabilização do lote baseado nas rubricas dos holerites
        """
        for lote in self:

            rubricas = self.gerar_rubricas_para_lancamentos_contabeis_lote()

            accout_move_ids = \
                lote.account_event_template_id.gerar_contabilizacao(rubricas)

            # Criar os relacionamentos
            for account_move_id in accout_move_ids:
                account_move_id.payslip_run_id = lote.id

            for line in accout_move_ids.mapped('line_id'):
                line.payslip_run_id = lote.id

            return True
