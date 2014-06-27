# -*- encoding: utf-8 -*-
##############################################################################
#
#    Brazillian Human Resources Payroll module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Matheus Felix <matheus.felix@kmee.com.br>
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
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp

class HrContract(orm.Model):
              
    _inherit='hr.contract'
    
    _columns = { 
        'food_voucher_amount': fields.float('Vale Alimentação', digits_compute=dp.get_precision('Payroll')),
        'meal_voucher_amount': fields.float('Vale Refeição', digits_compute=dp.get_precision('Payroll')),
        'workeddays': fields.float('Dias Trabalhados'),
        'transportation_voucher': fields.float('Vale Transporte'),  
        'health_insurance_father' : fields.float('Plano de Saúde do Empregado', help='Plano de Saúde do Funcionário'),
        'health_insurance_dependent' : fields.float('Plano de Saúde do Dependente', help='Plano de Saúde para os Cônjugues e Dependentes'),
        'dependents_ids': fields.one2many('hr.employee.dependent','employee_id', 'Dependent'),
        }
    
    
    comp_date = time.strftime('%Y-04-01')
    comp_date2 = time.strftime('%Y-02-28')
    

