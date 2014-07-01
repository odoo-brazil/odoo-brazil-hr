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
from IPython.parallel.controller.dependency import depend

class HrEmployee(osv.osv):
    
    ant_id = """e na qual reside nos últimos 05 anos)
        - quando aplicável ao projeto
    """
    cneg_id = """
        Certidões Negativas cíveis e criminais da 
        Justiça Federal (Da Cidade na qual reside nos últimos 05 anos) 
        - quando aplicável ao projeto
    """
    cnasc_id = """
        Certidões de Nascimento dos Filhos de até 14 anos
    """
    polcivil = """
        Certificado de Antecedentes expedido pela Polícia Civil - 
        Quando aplicável ao projeto
        Nada consta de antecedentes criminais cíveis, 
        de protestos de título de interdição e de turelas
        (cartório de distribuição da cidade na qual residiu nos últimos 05 anos)

    """
    cant_id = """
        Certificado de Antecedentes expedido pela 
        Polícia Federal (da cidade na qual reside nos últimos 05 anos)
        - quando aplicável ao projeto
    """
    cneg_id = """
        Certidões Negativas cíveis e criminais da 
        Justiça Federal (Da Cidade na qual reside nos últimos 05 anos) 
        - quando aplicável ao projeto
    """
    cnasc_id = """
        Certidões de Nascimento dos Filhos de até 14 anos
    """
    polcivil = """
        Certificado de Antecedentes expedido pela Polícia Civil - 
        Quando aplicável ao projeto
    """
    
    

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
                
        'check_cpolcivil': fields.boolean(polcivil),
        'check_casamento': fields.boolean('Certidão de Casamento'),
        'check_vacinacao': fields.boolean('Cartões de vacinação dos filhos com idades de até 06 anos'),
        'check_diploma': fields.boolean('Diplomas e Certificados que comprovem a formação acadêmica (Original e Cópia)'),
        'check_creservista': fields.boolean('Certificado de Reservista (Original e Cópia)'),
        'check_rg': fields.boolean('Carteira de Identidade (Original e Cópia)'),
        'check_cpf': fields.boolean('CPF (Original e Cópia)'),
        'check_eleitor': fields.boolean('Título de Eleitor (Original e Cópia)'),
        'check_ultvotacao': fields.boolean('Comprovante de Votação da Última Eleição (Original e Cópia)'),
        'check_ctecnica' : fields.boolean('Certificações Técnicas (Cópia Autenticada)'),
        'check_cquali': fields.boolean('Certificados de Qualificação e Aperfeiçoamento (Original e Cópia)'),
        'check_cres': fields.boolean('Comprovante de Residência (Original e Cópia)'),
        'check_cv' : fields.boolean('Currículo Vitae, Datado e Assinado'),
        'check_fotos' : fields.boolean('Duas Fotos 3x4 (Iguais e recentes com identificação no verso)'),
        'check_examedem' : fields.boolean('Exame Demissional (Último Empregador)'),
        'check_examead' : fields.boolean('Exame Admissional (Clínica do Convênio)'),
        'check_pis_pasep' : fields.boolean('PIS/PAESP N.º'),
        'check_cnasc' : fields.boolean('Certidões de Nascimento dos Filhos de até 14 anos'),
        'check_antecrim' : fields.boolean(ant_id),
        'check_cante' : fields.boolean(cant_id),
        'check_cnegciveis' : fields.boolean(cneg_id),
        'check_ctps': fields.boolean('Carteira de Trabalho com baixa do último empregador (Original e Cópia)'),
        'check_rg_obs': fields.char("Observação"),
        'check_ctps_obs': fields.char("Observação"),
        'check_cpf_obs': fields.char("Observação"),
        'check_antecrim_obs': fields.char("Observação"),
        'check_eleitor_obs': fields.char("Observação"),
        'check_ultvotacao_obs': fields.char("Observação"),
        'check_ctecnica_obs': fields.char("Observação"),
        'check_cquali_obs': fields.char("Observação"),
        'check_cres_obs': fields.char("Observação"),
        'check_cv_obs': fields.char("Observação"),
        'check_fotos_obs': fields.char("Observação"),
        'check_examead_obs': fields.char("Observação"),
        'check_examedem_obs': fields.char("Observação"),
        'check_pis_pasep_obs': fields.char("Observação"),
        'check_cnasc_obs': fields.char("Observação"),
        'check_antecrim_obs': fields.char("Observação"),
        'check_cante_obs': fields.char("Observação"),
        'check_cnegciveis_obs': fields.char("Observação"),
        'check_cpolcivil_obs': fields.char("Observação"),
        'check_casamento_obs': fields.char("Observação"),
        'check_vacinacao_obs': fields.char("Observação"),
        'check_diploma_obs': fields.char("Observação"),
        'check_creservista_obs': fields.char("Observação"),
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
    
