# -*- encoding: utf-8 -*-
##############################################################################
#
#    Brazillian Human Resources Payroll module for OpenERP
#    Copyright (C) 2014 KMEE (http://www.kmee.com.br)
#    @author Rafael da Silva Lima <rafael.lima@kmee.com.br>
#            Matheus Felix <matheus.felix@kmee.com.br>
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

from osv import fields,osv
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class HrEmployee(osv.osv):
     
    def _validate_pis_pasep(self, cr, uid, ids):
        employee = self.browse(cr, uid, ids[0])

        if not employee.pis_pasep:
            return True

        digits = []
        for c in employee.pis_pasep:
            if c == '.' or c == ' ' or c == '\t':
                continue

            if c == '-':
                if len(digits) != 10:
                    return False
                continue

            if c.isdigit():
                digits.append(int(c))
                continue

            return False
        if len(digits) != 11:
            return False

        height = [int(x) for x in "3298765432"]

        total = 0

        for i in range(10):
            total += digits[i] * height[i]

        rest = total % 11
        if rest != 0:
            rest = 11 - rest
        return (rest == digits[10])

#     def _calc_inss(self, cr, uid, ids, fields, arg, context=None):   
#         res = {}
#         obj_contract = self.pool.get('hr.contract')
#         contract1 = obj_contract.search(cr, uid, [('contract_id', '=', ids[0])])
#         contract = contract1.browse(cr, uid, contract1[0])
#         if contract:
#             res[ids[0]] = (-482.93 if ((contract.wage) >= 4390.25) else -((contract.wage) * 0.11) if ((contract.wage) >= 2195.13) and ((contract.wage) <= 4390.24) else -((contract.wage) * 0.09) if ((contract.wage) >= 1317.08) and ((contract.wage) <= 2195.12) else -((contract.wage) * 0.08))
#             return res
#         else:
#             return 0
    
    _inherit='hr.employee'

    _columns = {
        'pis_pasep': fields.char(u'PIS/PASEP', size=15),
        'ctps' : fields.char('CTPS', help='Número da carteira de trabalho profissional de serviço'), 
        'ctps_series' : fields.char('Série'),
        'ctps_date' : fields.date('Data de emissão'),
        'creservist': fields.char('Certificado de Reservista'),
        'crresv_categ': fields.char('Categoria'),
        'cr_categ': fields.selection([('estagiario', 'Estagiario'), ('junior', 'Júnior'),
                                        ('pleno', 'Pleno'), ('sênior', 'Sênior')], 'Categoria'
                                    , help="Escolha a Categoria de Instrução:"),
        'ginstru': fields.selection([('fundamental_incompleto', 'Ensino Fundamental Incompleto'), ('fundamental', 'Ensino Fundamental Completo '),
                    ('medio_incompleto', 'Ensino Médio Incompleto'),
                    ('medio', 'Ensino Médio Completo'),
                    ('superior_incompleto', 'Curso Superior Incompleto'),
                    ('superior', 'Curso Superior Completo'),
                    ('mestrado', 'Mestrado '),
                    ('doutorado', 'Doutorado')], 'Nível de Escolaridade',
                                help="Escolha o grau de instrução"),
        
        'have_dependent': fields.boolean("Associados"),
        'dependent_ids': fields.one2many('hr.employee.dependent', 'employee_id', 'Employee'),
        'rg': fields.char('RG', help='Número do RG'),
        'organ_exp': fields.char("Orgão de Expedição"),
        'rg_emission': fields.date('Data de Emissão'),
        'title_voter': fields.char('Título', help='Número do Título Eleitor'),
        'zone_voter': fields.char('Zona'),
        'session_voter': fields.date('Seção'),
        'driver_license': fields.char('Carteira de Motorista', help='Numero da Carteira Motorista'),
        'driver_categ':fields.char('Categoria'),
        'father_name': fields.char('Nome do Pai'),
        'mother_name': fields.char('Nome da Mãe'),
        'number_dependent': fields.integer("Dependentes"),
    }    

    _constraints = [[_validate_pis_pasep, u'Número PIS/PASEP é inválido.', ['pis_pasep']]] 
    
   

class HrEmployeeDependent(osv.osv):
    _name = 'hr.employee.dependent'
    _description='Employee\'s Dependents'
    
    def _check_birth(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if datetime.strptime(obj.dependent_age, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
            return False
        return True
    
     
    _columns = {
        'employee_id' : fields.many2one('hr.employee', 'Employee'),
        'dependent_name' : fields.char('Name', size=64, required=True, translate=True),
        'dependent_age' : fields.date('Data de Nascimento', required=True),
        'dependent_type': fields.char('Tipo do Associoado', required=True),
        'pension_benefits': fields.float('Pensão Alimenticia'),
        'dependent_verification': fields.boolean('É dependente', required=False),
        'health_verification': fields.boolean('Plano de Saúde', required=False),
       }
    
    _constraints = [[_check_birth, u'Data de Nascimento está no futuro!', ['dependent_age']]] 
    
