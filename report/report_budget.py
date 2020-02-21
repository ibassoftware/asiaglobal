from odoo import tools
from odoo import api, fields, models

class AccountBudgetReport(models.Model):
	_name = "accout.budget.report"
	_description = "Budget Analysis"
	_auto = False
	_rec_name = 'date'
	_order = 'date desc'

	name = fields.Char()
	date = fields.Date()
	general_budget_id = fields.Many2one('account.budget.post')
	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	amount_budget = fields.Float(string='Budget')
	amount_actual = fields.Float(string='Actual')
	variance = fields.Float()
	variance_percent = fields.Integer(string='Percentage of Variance')
	analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line')

