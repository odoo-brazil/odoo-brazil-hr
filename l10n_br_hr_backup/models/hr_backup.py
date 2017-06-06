# -*- coding: utf-8 -*-
# Copyright (C) 2017 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
import os
import re

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class HrBackup(models.Model):
    _name = 'hr.backup'

    @api.multi
    def get_external_id(self, object, name):
        """
        Retorna a referencia externa se existir senao retorna o nome
        passado como parametro
        :param object: instancia do objeto
        :param name:   str - nome do record ex.: hr_salary_rule_RUBRICA01
        """
        if object._get_external_ids().get(object.id):
            return object._get_external_ids().get(object.id)[0]
        return name

    @api.multi
    def registrar_modelo_ir_model_data(self, objeto, name=False):
        """
        Função que registra na tabela ir_model_data a existencia do objeto que
        foi criado via interface
        :param objeto: Objeto a ser registrado
        :param name: nome do objeto a ser registrado na tabela,
        :return: instancia do ir_model_data
        """
        ir_model_data_obj = self.env['ir.model.data']

        # Se nao passar nenhum nome no parametro, utilizar o nome do objeto
        if not name:
            name = objeto._name

        vals = {
            'name': name,
            'module': 'l10n_br_hr_backup',
            'model': objeto._model,
            'res_id': objeto.id,
        }

        return ir_model_data_obj.create(vals)

    @api.multi
    def escrever_arquivo_backup(self, name, texto):

        template_path = '{}/../data/' + name + '.xml'
        template_path = template_path.format(os.path.dirname(__file__))

        xml_antigo = open(template_path, 'r')
        xml_antigo = xml_antigo.read()

        if xml_antigo:
            # Remover as TAGS de fechamento do arquivo
            xml_antigo = re.sub('\<\/data>', '', xml_antigo)
            xml_antigo = re.sub('\<\/openerp>', '', xml_antigo)
        else:
            xml_antigo = '\t<openerp>\n\t\t<data>\n'

        xml_final = xml_antigo + '\t\t<!-- BACKUP EM  '
        xml_final += str(fields.datetime.now()) + ' -->\n'
        xml_final += texto
        xml_final += '\t\t</data>\n\t</openerp>\n'

        backup_xml = open(template_path, 'w')
        backup_xml.write(xml_final)
        # backup_xml.write(xml_final.encode('utf-8'))
        backup_xml.close()

    @api.multi
    def gerar_backup_regras_criadas(self):
        """
        Função que busca as regras que foram criadas somente pela interface,
        dispara uma função para registro na tabela ir_model_data e retorna um
        texto em xml para gerar o backup das regras
        # <record(.|\s)*?record>
        """
        hr_salary_rule_obj = self.env['hr.salary.rule']
        ir_model_data_obj = self.env['ir.model.data']

        # Buscar todas as regras que foram geradas apartir do XML
        res_id =  ir_model_data_obj.search([
            ('model', '=', 'hr.salary.rule'),
        ]).mapped('res_id')

        # Identificar regras geradas pela interface
        regras_sem_xml = hr_salary_rule_obj.search([
            ('id', 'not in', res_id),
        ])

        # variavel que contem as regras em xml
        regras_xml = u''

        for regra_sem_xml in regras_sem_xml:
            # Se nao achar um id externo cria na tabela ir_model_data
            if not self.get_external_id(regra_sem_xml, False):
                name = 'hr_salary_rule_' + regra_sem_xml.code
                self.registrar_modelo_ir_model_data(regra_sem_xml, name)
                regras_xml += regra_sem_xml.generate_xml

        return regras_xml.encode('utf-8'), len(regras_sem_xml)

    @api.multi
    def gerar_backup_regras_editadas(self):
        """
        Função que gera um texto no formato xml para realizar o backup
        """
        hr_salary_rule_obj = self.env['hr.salary.rule']

        regras = hr_salary_rule_obj.search([])

        regras_xml = u''
        regras_qty = 0
        for regra in regras:
            if regra.create_date != regra.write_date:
                if not regra.last_backup or \
                                regra.write_date > regra.last_backup:
                    regras_xml += regra.generate_xml
                    regras_qty += 1
                    regra.last_backup = fields.datetime.now()
        return regras_xml.encode('utf-8'), regras_qty

    @api.multi
    def gerar_backup(self):
        """
        Rotina chamada pela interface que faz backup das regras de salario
        """
        # Gerar xml com todas as regras criadas via interface
        xml_regras_criadas, qty_regras_criadas = \
            self.gerar_backup_regras_criadas()

        # Gerar xml com todas as regras editadas via interface
        xml_regras_editadas, qty_regras_editadas = \
            self.gerar_backup_regras_editadas()

        # Ajustar estrutura do xml
        xml_regras = '\n\t\t<!-- Regras Criadas: %d --> \n\n' % \
                     qty_regras_criadas
        xml_regras += xml_regras_criadas
        xml_regras += '\n\t\t<!-- Regras Editadas: %d --> \n\n' % \
                      qty_regras_editadas
        xml_regras += xml_regras_editadas

        # Escreve no arquivo XML do modulo
        self.escrever_arquivo_backup('hr_salary_rule', xml_regras)
