from odoo import tools
from odoo import api, fields, models

class AccountBudgetReport(models.Model):
	_name = "account.budget.report"
	_description = "Budget Analysis"
	_auto = False
	_rec_name = 'date'
	_order = 'date desc'

	name = fields.Char()
	date = fields.Date()
	general_budget_id = fields.Many2one('account.budget.post')
	crossovered_budget_id = fields.Many2one('crossovered.budget')
	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	amount_budget = fields.Float(string='Budget')
	amount_actual = fields.Float(string='Actual')
	variance = fields.Float()
	variance_percent = fields.Integer(string='Percentage of Variance')
	# analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line')

	def _select(self):
		# crossovered_budget = self.env['crossovered.budget'].search([('state','=','validate')])
		# account_ids = crossovered_budget.mapped('general_budget_id').mapped('account_ids').ids
		select_str = """
			SELECT l.id as id,
				l.name as name,
				l.date as date,
				l.amount as amount_actual, 
				l.account_id as analytic_account_id,
				cb.id as crossovered_budget_id,
				bp.id as general_budget_id,
				sum(cbl.planned_amount) as amount_budget,
				sum(l.amount - cbl.planned_amount) as variance,
				sum((l.amount - cbl.planned_amount) / cbl.planned_amount * 100) as variance_percent
		"""
		return select_str

	def _from(self):
		from_str = """
			account_analytic_line l
				left join crossovered_budget_lines cbl on (cbl.analytic_account_id=l.account_id)
				left join crossovered_budget cb on (cb.id=cbl.crossovered_budget_id)
				left join account_budget_post bp on (bp.id=cbl.general_budget_id)
		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY l.id,
				l.name,
				l.date,
				l.amount,
				l.account_id,
				cb.id,
				bp.id
		"""
		return group_by_str

	@api.model_cr
	def init(self):
		# self._table = sale_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			FROM ( %s )
			%s
			)""" % (self._table, self._select(), self._from(), self._group_by()))