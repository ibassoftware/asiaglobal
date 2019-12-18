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
	is_copied = fields.Boolean(copy=False)

	serial_number = fields.Char(related='jo_id.serial_number', string='Serial Number of Unit')

	def action_duplicate(self):
		timesheet_ids = [(0,0, {
			'activity_type': self.activity_type.id,
			'technician_id': self.technician_id.id,
			'name': self.name,
			'date': self.date,
			'unit_amount': self.unit_amount,
			'is_copied': True,
		})]
		
		# # self.env['asiaglobal.service_timesheet'].create({
		# # 	'jo_id': self.jo_id.id,
		# # 	'activity_type': self.activity_type.id,
		# # 	'technician_id': self.technician_id.id,
		# # 	'name': self.name,
		# # 	'date': self.date,
		# # 	'unit_amount': self.unit_amount,
		# # })
		self.jo_id.timesheet_ids = timesheet_ids
