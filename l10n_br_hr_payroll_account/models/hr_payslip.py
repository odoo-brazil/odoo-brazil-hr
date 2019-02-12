# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# Copyright (C) 2018 ABGF (http://www.abgf.gov.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import absolute_import, print_function, unicode_literals

from openerp import api, models, fields, _
from openerp.exceptions import Warning


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
        contabilizacao_rubricas = {}

        # Roda as Rubricas e Cria os lançamentos contábeis
        for line in self.line_ids:
            if line.salary_rule_id.gerar_contabilizacao:
                contabilizacao_rubricas[line.salary_rule_id.code] = line.total

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

            holerite.account_event_template_id.gerar_contabilizacao(
                rubricas_para_contabilizar)
