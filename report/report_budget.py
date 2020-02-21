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
	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	amount_budget = fields.Float(string='Budget')
	amount_actual = fields.Float(string='Actual')
	variance = fields.Float()
	variance_percent = fields.Integer(string='Percentage of Variance')
	analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line')

	def _select(self):
		select_str = """
			SELECT l.name as name,
				l.date as date,
				l.amount as amount_actual,
				t.uom_id as product_uom
		"""
		return select_str

	def _from(self):
		from_str = """
				account_analytic_line l
		"""
		return from_str

	# def _group_by(self):
	# 	group_by_str = """
	# 		GROUP BY l.date,
	# 	"""
	# 	return group_by_str

	@api.model_cr
	def init(self):
		# self._table = sale_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( %s FROM %s )""" % (self._table, self._select(), self._from()))