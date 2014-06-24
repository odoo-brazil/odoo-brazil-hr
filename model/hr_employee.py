    # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - KMEE- Rafael da Silva Lima (<http://www.kmee.com.br>)
#                              
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

    
    _inherit='hr.employee'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),   
        'pis_pasep': fields.char(u'PIS/PASEP', size=15),
        'ctps' : fields.char('CTPS', help='Número da carteira de trabalho profissional de serviço'), 
        'ctps_serie' : fields.char('Série'),
        'ctps_data' : fields.date('Data de emissão'),
        'creservista': fields.char('Certificado de Reservista'),
        'crresv_categ': fields.char('Categoria'),
        'cr_categ': fields.selection([('estagiario', 'Estagiario'), ('junior', 'Júnior'),
                                        ('pleno', 'Pleno'), ('sênior', 'Sênior')], 'Categoria'
                                    , help="Escolha a Categoria de Instrução:"),
        'ginstru': fields.selection([('fundamental_incompleto', 'Ensino fundamental incompleto'), ('fundamental', 'Ensino fundamental completo '),
                    ('medio_incompleto', 'Ensino médio incompleto'),
                    ('medio', 'Ensino médio completo'),
                    ('superior_incompleto', 'Curso superior incompleto'),
                    ('superior', 'Curso superior completo'),
                    ('mestrado', 'Mestrado '),
                    ('doutorado', 'Doutorado')], 'Nível de Escolaridade',
                                help="Escolha o grau de instrução"),
        
        'nome_conju': fields.char("Nome do Cônjuge"),
        'tem_filhos': fields.boolean("Possui dependentes"),  
        'filhos_ids': fields.one2many('hr.employee.childs', 'employee_id', 'Employee'),
        'rg': fields.char('RG', help='Número do RG'),
        'orgao_exp': fields.char("Orgão de Expedição"),
        'rg_emissao': fields.date('Data de Emissão'),
        'titulo': fields.char('Título', help='Número do Título Eleitor'),
        'zona': fields.char('Zona'),
        'secao': fields.date('Seção'),
        'cart_motorista': fields.char('Carteira de Motorista', help='Numero da Carteira Motorista'),
        'categ_mot':fields.char('Categoria'),
        'nome_pai': fields.char('Nome do Pai'),
        'nome_mae': fields.char('Nome da Mãe')
    }

    _constraints = [[_validate_pis_pasep, u'Número PIS/PASEP é inválido.', ['pis_pasep']]] 
    
class HrEmployeeChilds(osv.Model):
    _name = 'hr.employee.childs'
    _description='Employee\'s Childs'
    
    def _check_birth(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if datetime.strptime(obj.filho_idade, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
            return False
        return True

    _columns = {
        'employee_id' : fields.many2one('hr.employee', 'Employee'),
        'filho_nome' : fields.char('Name', size=64, required=True, translate=True),
        'filho_idade' : fields.date('Birthday', required=True, translate=True),
        'pensao_alimenticia': fields.char('Pensão Alimenticia', required=True, translate=True),
        'disable_children': fields.boolean('Deficiente')
        }

    _constraints = [[_check_birth, u'Data de Nascimento está no futuro!', ['filho_idade']]] 
