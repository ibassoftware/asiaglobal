from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AsiaGlobalTimesheetActivityType(models.Model):
	_name = 'asiaglobal.timesheet_activity_type'
	_description = 'Timesheet Activity Type'

	name = fields.Char(required=True)
	billable = fields.Boolean()

# class AsiaGlobalTimesheetAnalyticLine(models.Model):
# 	_inherit = 'account.analytic.line'

# 	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')
# 	activity_type = fields.Many2one('asiaglobal.timesheet_activity_type')

# 	def _timesheet_preprocess(self, vals):
# 		""" Deduce other field values from the one given.
# 			Overrride this to compute on the fly some field that can not be computed fields.
# 			:param values: dict values for `create`or `write`.
# 		"""
# 		if vals.get('jo_id') and not vals.get('account_id'):
# 			account = self.env['account.analytic.account'].search([('code', '=', 'AGT-JO')], limit=1)
# 			vals['account_id'] = account.id

# 		result = super(AsiaGlobalTimesheetAnalyticLine, self)._timesheet_preprocess(vals)
# 		return result

class AsiaGlobalServcieTimesheet(models.Model):
	_name = 'asiaglobal.service_timesheet'

	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')
	activity_type = fields.Many2one('asiaglobal.timesheet_activity_type')
	technician_id = fields.Many2one('hr.employee', "Employee")

	name = fields.Char('Description', required=True)
	date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
	unit_amount = fields.Float('Quantity', default=0.0)

	def action_duplicate(self):
		self.copy()