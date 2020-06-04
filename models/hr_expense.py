from odoo import models, fields, api, _ 
from odoo.addons import decimal_precision as dp

class HrExpenseSheet(models.Model):
	_inherit = 'hr.expense.sheet'

	expense_line_ids = fields.One2many(states={'done': [('readonly', True)], 'post': [('readonly', True)]})
	
class HrExpense(models.Model):
	_inherit = 'hr.expense'

	unit_amount = fields.Float(digits=dp.get_precision('Sale Product Price'))