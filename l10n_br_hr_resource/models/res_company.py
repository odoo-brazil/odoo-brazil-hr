# -*- coding: utf-8 -*-
# Copyright 2018 ABGF - Hendrix Costa <hendrix.costa@abgf.gov.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from openerp import api, exceptions, fields, models, _


class ResCompany(models.Model):
    """Override company to activate validate phones"""
    _inherit = "res.company"

    default_resource_calendar_id = fields.Many2one(
        string=u'Calendário Padrão',
        comodel_name=u'resource.calendar',
        help=u'Calendário que indica os feriados padrões da empresa.',
    )
