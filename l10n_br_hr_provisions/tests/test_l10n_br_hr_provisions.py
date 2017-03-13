# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields
from openerp.tests import common


class TestL10nBrHrProvisions(common.TransactionCase):

    def setUp(self):
        super(TestL10nBrHrProvisions, self).setUp()
        # Usefull models
        self.hr_employee = self.env['hr.employee']
        self.resource_calendar = self.env['resource.calendar']
        self.hr_contract = self.env['hr.contract']
        self.hr_job = self.env['hr.job']
        self.hr_payslip = self.env["hr.payslip"]
        self.hr_payroll_structure = self.env["hr.payroll.structure"]
        self.hr_payslip_worked_days = self.env['hr.payslip.worked_days']
        group_employee_id = self.ref('base.group_user')
        self.hr_holidays = self.env['hr.holidays']
        self.funcao_comissionada = self.ref(
            'l10n_br_hr_payroll.hr_salary_structure_FUNCAO_COMISSIONADA'
        )

        # Funcionario Comissionado
        self.employee_hr_user_id = self.hr_employee.create({
            'name': 'Employee Luiza',
        })
        # calendario padrao nacional
        self.nacional_calendar_id = self.resource_calendar.create({
            'name': 'Calendario Nacional',
            'country_id': self.env.ref("base.br").id,
        })

    def criar_contrato(self, nome, wage, struct_id, employee_id, job_name):
        self.job_id = self.hr_job.create({'name': job_name})
        hr_contract_id = self.hr_contract.create({
            'name': nome,
            'employee_id': employee_id.id,
            'job_id': self.job_id.id,
            'type_id': self.env.ref('hr_contract.hr_contract_type_emp').id,
            'wage': wage,
            'date_start': '2017-01-01',
            'working_hours': self.nacional_calendar_id.id,
            'struct_id': struct_id,
        })
        return hr_contract_id

    def criar_folha_pagamento(self, date_from, date_to, contract_id,
                              employee_id):

        hr_payslip_id = self.hr_payslip.create({
            'employee_id': employee_id,
            'date_from': date_from,
            'date_to': date_to,
            'contract_id': contract_id,
        })
        return hr_payslip_id

    def processar_folha_pagamento(self, hr_payslip):
        # Processando a folha de pagamento
        result = hr_payslip.onchange_employee_id(
            hr_payslip.date_from, hr_payslip.date_to,
            hr_payslip.employee_id.id, hr_payslip.contract_id)
        worked_days_line_ids = []
        for line in result['value']['worked_days_line_ids']:
            worked_days_line_ids_obj = self.hr_payslip_worked_days.create({
                'name': line['name'],
                'sequence': line['sequence'],
                'code': line['code'],
                'number_of_days': line['number_of_days'],
                'number_of_hours': line['number_of_hours'],
                'contract_id': line['contract_id'],
                'payslip_id': hr_payslip.id,
            })
            worked_days_line_ids.append(worked_days_line_ids_obj)
        hr_payslip.compute_sheet()

    def test_criar_contrato(self):
        """Teste para criar um novo contrato"""
        contract_id = self.criar_contrato(
            self.employee_hr_user_id.name,
            7000,
            self.funcao_comissionada,
            self.employee_hr_user_id,
            'Analista de Sistemas'
        )
        teste = ""
