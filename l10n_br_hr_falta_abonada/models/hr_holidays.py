from openerp import api, fields, models, _


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    ano = fields.Integer(
        string=u'Ano referência',
    )