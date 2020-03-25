from odoo import models, fields, api, _ 

class HrExpenseSheet(models.Model):
	_inherit = 'hr.expense.sheet'

	expense_line_ids = fields.One2many(states={'done': [('readonly', True)], 'post': [('readonly', True)]})