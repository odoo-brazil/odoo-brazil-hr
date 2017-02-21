# -*- coding: utf-8 -*-
# Copyright 2017 Sei lá
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def gerar_credito_faltas_abonadas(self):
        dominio = [
            '|',
            ('date_end', '=', False),
            ('date_end', '>', fields.Date.today()),
        ]
        contratos_ativos = self.env['hr.contract'].search(dominio)
        for contrato in contratos_ativos:
            falta_abonada_id = contrato.env.ref(
                'l10n_br_hr_falta_abonada.holiday_status_falta_abonada_anual').id
            falta_abonada = contrato.env['hr.holidays'].create({
                'name': 'Faltas abonadas %s'
                        % datetime.now().year,
                'employee_id': contrato.employee_id.id,
                'holiday_status_id': falta_abonada_id,
                'type': 'add',
                'holiday_type': 'employee',
                'number_of_days_temp': 5,
                'ano': datetime.now().year,
            })
            falta_abonada.state = 'validate'
        
    @api.model
    def create(self, vals):
        contrato = super(HrContract, self).create(vals)
        self.gerar_credito_faltas_abonadas()
        return contrato