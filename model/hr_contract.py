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
        
    def _check_voucher(self, cr, uid, ids, context=None):    
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
           
        for contract in self.browse(cr, uid, ids):
            if user.company_id.check_benefits:
                return True
            else:
                if contract.value_va == 0 or contract.value_vr == 0:
                    return True
                else:
                    return False
        return True       
          
    _columns = { 
        'value_va': fields.float('Vale Alimentação', help='Valor Diário do Benefício'),        
        'value_vr': fields.float('Vale Refeição', help='Valor Diário do Benefício'),  
        'workeddays': fields.function(_get_worked_days, type='float'),
        'transportation_voucher': fields.float('Vale Transporte', help='Porcentagem de desconto mensal'),  
        'health_insurance_father' : fields.float('Plano de Saúde do Empregado', help='Plano de Saúde do Funcionário'),
        'health_insurance_dependent' : fields.float('Plano de Saúde do Dependente', help='Plano de Saúde para os Cônjugues e Dependentes'),
        'calc_date': fields.function(_check_date, type='boolean'),
        }
    
    _constraints = [[_check_voucher, u'As configurações da empresa não permitem o uso de vale alimentação e refeição simultâneos', ['value_va', 'value_vr']]]
    
    _defaults = {
        'value_va' : 0, 
        'value_vr' : 0  
    }
    

    
     

   
    

