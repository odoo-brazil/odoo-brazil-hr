# -*- coding: utf-8 -*-
# Copyright (C) 2016 KMEE (http://www.kmee.com.br)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import unicode_literals, division, print_function

import logging
import re

from openerp import api
from openerp import fields, models

_logger = logging.getLogger(__name__)

try:
    from pybrasil.python_pt_BR import python_pt_BR
    from pybrasil.valor.decimal import Decimal

except ImportError:
    _logger.info('Cannot import pybrasil')


class HrSalaryRule(models.Model):
    _inherit = b'hr.salary.rule'

    @api.multi
    def formata_caracteres_xml(self, field):
        """
        Formata o XML que nao pode conter caracateres como '<=' ou '>='
        """
        # Validar a entrada de dados
        if not isinstance(field, (str, unicode)):
            return field

        # Menor igual
        field = re.sub('<=', ' &lt;= ', field)
        # Menor
        field = re.sub('<[^/ford!?]', ' &lt; ', field)
        # Maior Igual
        field = re.sub('>=', ' &gt;= ', field)
        # Maior
        field = re.sub('[^pad?"\-/] >', ' &gt; ', field)

        return field

    @api.multi
    def _compute_xml_rubrica(self):
        """
        Função que gera XML da rubrica atual
        """

        for regra in self:

            # Se a regra ja tiver identificação no ir_model_data exibe a
            # external_id, senão exibe a external id que sera criada pelo
            # modulo de backup
            backup = self.env['hr.backup']
            id = backup.get_external_id(
                regra, 'hr_salary_rule_%s' % regra.code)

            record = \
                "\t\t<record id=\"%s\" model=\"hr.salary.rule\"> \n" % id
            record += "\t\t\t<field name=\"code\">%s</field>\n" % (regra.code)
            record += "\t\t\t<field name=\"name\">%s</field>\n" % (regra.name)
            record += "\t\t\t<field name=\"category_id\" ref=\"%s\"/>\n" % \
                      (regra.category_id._get_external_ids().
                       get(regra.category_id.id)[0])

            record += "\t\t\t<field name=\"active\" eval=\"%s\"/>\n" %\
                      (regra.active)

            record += "\t\t\t<field name=\"condition_select\">%s</field>\n" %\
                      (regra.condition_select)

            record += "\t\t\t<field name=\"condition_python\">%s</field>\n" % \
                      (self.formata_caracteres_xml(regra.condition_python))

            record += "\t\t\t<field name=\"amount_select\">%s</field>\n" % \
                      (regra.amount_select)

            record += "\t\t\t<field name=\"custom_amount_select\">%s</field>\n" % \
                      (regra.custom_amount_select)

            record += \
                "\t\t\t<field name=\"amount_python_compute\">%s</field>\n" % \
                (self.formata_caracteres_xml(regra.amount_python_compute))

            record += \
                "\t\t\t<field name=\"custom_amount_python_compute\">%s</field>\n" % \
                (self.formata_caracteres_xml(regra.custom_amount_python_compute))

            record += "\t\t\t<field name=\"sequence\" eval=\"%d\" />\n" % \
                      (regra.sequence)
            record += \
                "\t\t\t<field name=\"compoe_base_INSS\" eval=\"%s\"/>\n" % \
                      (regra.compoe_base_INSS)
            record += "\t\t\t<field name=\"compoe_base_IR\" eval=\"%s\"/>\n" % \
                      (regra.compoe_base_IR)
            record += "\t\t\t<field name=\"compoe_base_FGTS\" eval=\"%s\"/>\n" %\
                      (regra.compoe_base_FGTS)

            record += "\t\t\t<field name=\"amount_fix\">%s</field>\n" % \
                      (regra.amount_fix)

            record += "\t\t\t<field name=\"custom_amount_fix\">%s</field>\n" % \
                      (regra.custom_amount_fix)

            record += "\t\t\t<field name=\"amount_percentage\">%s</field>\n" % \
                      (regra.amount_percentage)

            record += "\t\t\t<field name=\"amount_percentage_base\">%s</field>\n" % \
                      (regra.amount_percentage_base)

            record += "\t\t\t<field name=\"custom_amount_percentage_base\">%s</field>\n" % \
                      (regra.custom_amount_percentage_base)

            record += "\t\t\t<field name=\"custom_amount_percentage\">%s</field>\n" % \
                      (regra.custom_amount_percentage)

            record += "\t\t\t<field name=\"appears_on_payslip\" eval=\"%s\"/>\n" %\
                      (regra.appears_on_payslip)

            record += "\t\t\t<field name=\"condition_range\">%s</field>\n" % \
                      (regra.condition_range)

            record += "\t\t\t<field name=\"condition_range_min\">%s</field>\n" % \
                      (regra.condition_range_min)

            record += "\t\t\t<field name=\"condition_range_max\">%s</field>\n" % \
                      (regra.condition_range_max)

            record += "\t\t\t<field name=\"note\">%s</field>\n" % \
                      (regra.note)

            record += "\t\t\t<field name=\"calculo_nao_padrao\" eval=\"%s\"/>\n" %\
                      (regra.calculo_nao_padrao)

            record += "\t\t\t<field name=\"quantity\">%s</field>\n" % \
                      (regra.quantity)

            record += "\t\t\t<field name=\"custom_quantity\">%s</field>\n" % \
                      (regra.custom_quantity or '')

            # record += "\t\t\t<field name=\"company_id\" eval=\"%s\"/>\n" %\
            #           (regra.company_id)
            # record += "\t\t\t<field name=\"register_id\" eval=\"%s\"/>\n" %\
            #           (regra.register_id)
            # record += "\t\t\t<field name=\"parent_rule_id\" eval=\"%s\"/>\n" %\
            #           (regra.parent_rule_id)

            record += "\t\t\t<field name=\"tipo_media\">%s</field>\n" % \
                      (regra.tipo_media or '')

            record += "\t\t</record>\n\n"

            regra.generate_xml = record
        
    generate_xml = fields.Text(
        string='XML da rubrica gerado automaticamente',
        compute='_compute_xml_rubrica',
        help='Cole esse xml em seu modulo',
    )

    last_backup = fields.Datetime(
        string='Data do ultimo backup',
    )

    @api.multi
    def gerar_backup(self):
        self.env['hr.backup'].gerar_backup()
