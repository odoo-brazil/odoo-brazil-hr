# -*- encoding: utf-8 -*-
##############################################################################
#
#    Brazillian Human Resources Payroll module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Matheus Felix <matheus.felix@kmee.com.br>
#            Rafael da Silva Lima <rafael.lima@kmee.com.br>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
import time

class HrContract(orm.Model):
              
    _inherit='hr.contract'
    
    def _get_worked_days(self, cr, uid, ids, fields, arg, context=None):   
        res = {}
    
        obj_worked_days = self.pool.get('hr.payslip.worked_days')
        worked_ids =  obj_worked_days.search(cr, uid, [('contract_id', '=', ids[0])])
        if worked_ids:
            worked = obj_worked_days.browse(cr, uid, worked_ids[0])
            res[ids[0]] = worked.number_of_days
            return res
        else:
            res[ids[0]] = 0
            return res
    
    def _check_date(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        
        comp_date_from = time.strftime('%Y-04-01')
        comp_date_to = time.strftime('%Y-02-28')
        obj_payslip = self.pool.get('hr.payslip')
        payslip_ids = obj_payslip.search(cr, uid, [('contract_id', '=', ids[0]),
                                                   ('date_from', '<', comp_date_from),
                                                   ('date_to', '>', comp_date_to)])
        if payslip_ids:
            res[ids[0]] = True
            return res    
        else:
            res[ids[0]] = False
            return res 
        
    def _check_amount(self, cr, uid, ids, fields, arg, context=None):

        res = {}
        obj_contract = self.pool.get('hr.contract')
        amount_ids = obj_contract.search(cr, uid, [
                                               ('value_amount', '>', 0)])
        pens = self.browse(cr, uid, amount_ids[0], context)    
        
        if pens.voucher_amount==pens.vr:
            res[ids[0]] = pens.value_amount
            return res    
        else:
            res[ids[0]] = pens.value_amount
            return res  
           
    _columns = { 
        'voucher_amount': fields.selection([('va', 'Vale Alimentação'),
                    ('vr', 'Vale Refeição'),],
                    'Tipo de Vale'),
        'value_amount': fields.float('Valor', help='Valor Diário do Benefício'),        
        'workeddays': fields.function(_get_worked_days, type='float'),
        'transportation_voucher': fields.float('Vale Transporte'),  
        'health_insurance_father' : fields.float('Plano de Saúde do Empregado', help='Plano de Saúde do Funcionário'),
        'health_insurance_dependent' : fields.float('Plano de Saúde do Dependente', help='Plano de Saúde para os Cônjugues e Dependentes'),
        'dependents_ids': fields.one2many('hr.employee.dependent','employee_id', 'Dependent'),
        
        'calc_date': fields.function(_check_date, type='boolean'),
        'check_amount': fields.function(_check_amount, type='float')
        
        }
    
   
    
    

   
    

