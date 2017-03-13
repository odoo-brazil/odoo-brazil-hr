# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from openerp.addons.l10n_br_hr_payroll.models.hr_payslip import TIPO_DE_FOLHA

TIPO_DE_FOLHA.append(('provisao_ferias', u'Provisão de Férias'))


class L10nBrHrProvisions(models.Model):
    _inherit = 'hr.payslip'

    tipo_de_folha = fields.Selection(
        selection=TIPO_DE_FOLHA,
        string=u'Tipo de folha',
        default='normal',
    )
