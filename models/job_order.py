from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class AsiaGlobalJobOrder(models.Model):
	_name = 'asiaglobal.job_order'
	_description = 'Job Order'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	initial_complaint = fields.Text()
	customer_id = fields.Many2one('res.partner', string='Customer')
	ship_to = fields.Many2one('res.partner', string='Ship To / Site Address')

	# type = fields.Selection([
	# 	('proactive','Proactive'),
	# 	('reactive','Reactive')
	# ], string="Department")
	type = fields.Selection([
		('weqd','WEQD'),
		('heqd','HEQD'),
		('rental','RENTAL'),
	], string="Department")

	initial_diagnosis = fields.Text()
	technician_id = fields.Many2one('hr.employee', string='Primary Technician', domain=[('is_technician','=',True)])
	ticket_ids = fields.One2many('helpdesk.ticket', 'jo_id', string='Helpdesk Tickets')
	state = fields.Selection([
		('draft','New'),
		('schedule','For Scheduling'),
		('progress', 'In Progress'),
		('bill', 'For Billing'),
		('done','Done'),
		], string='Status', default='draft')
	sale_ids = fields.One2many('sale.order', 'jo_id', string='Sale Orders')
	under_warranty = fields.Boolean()
	warranty_date = fields.Date(default=fields.Datetime.now())

	equipment_id = fields.Many2one('asiaglobal.equipment_profile', string='Equipment')
	manufacturer = fields.Many2one('asiaglobal.manufacturer', string='Manufacturer')
	model = fields.Many2one('asiaglobal.manufacturer_model', string='Model')
	serial_number = fields.Char()
	scheduled_date = fields.Date(default=fields.Datetime.now())
	actual_repair_date = fields.Date(default=fields.Datetime.now())

	service_report_ids = fields.One2many('asiaglobal.service_report', 'jo_id')
	legacy_jo_no = fields.Char(string='Legacy Number')

	# job_classification = fields.Selection([
	# 	('weqd','WEQD'),
	# 	('heqd','HEQD'),
	# 	('rental','RENTAL'),
	# ])

	job_classification = fields.Selection([
		('Internal','Internal'),
		('external','External'),
		('warranty','Warranty'),
	])

	job_type = fields.Selection([
		('maintenance','Prev Maintenance'),
		('inspection','Diagnostics Inspection'),
		('repair','Repair'),
		('assembly','Assembly/Delivery'),
	])

	operational = fields.Boolean()

	timesheet_ids = fields.One2many('asiaglobal.service_timesheet', 'jo_id')

	@api.onchange('equipment_id')
	def set_equipment_details(self):
		_logger.info('UNDERWA')
		if self.equipment_id:
			self.ship_to = self.equipment_id.ship_to
			self.manufacturer = self.equipment_id.manufacturer
			self.model = self.equipment_id.model
			self.serial_number = self.equipment_id.serial_number
			self.operational = self.equipment_id.operational

			# SET WARRANTY DETAILS
			date_today = datetime.now()
			date_acceptance = datetime.strptime(self.equipment_id.warranty_date_acceptance, '%Y-%m-%d')
			warranty_year = self.equipment_id.warranty_year
			warranty_hours = self.equipment_id.warranty_hours

			year = int(warranty_year)
			month = str(warranty_year-int(warranty_year))[1:]
			month = round(float(month) * 10)
			_logger.info(year)
			_logger.info(month)

			hours = int(warranty_hours)
			minutes = str(warranty_hours-int(warranty_hours))[1:]
			minutes = round(float(minutes) * 60)
			_logger.info(hours)
			_logger.info(minutes)

			# warranty_date = (date_acceptance + relativedelta(years=year) + timedelta(hours=hours))
			warranty_date = (date_acceptance + relativedelta(years=year)) #YEARS
			warranty_date = (warranty_date + relativedelta(months=month)) #YEARS
			warranty_date = (warranty_date + timedelta(hours=hours))
			
			if date_today <= warranty_date:
				self.under_warranty = True
				self.warranty_date = warranty_date
			else:
				self.under_warranty = False
				self.warranty_date = False


	# @api.onchange('job_classification')
	# def set_classification_details(self):
	# 	if self.job_classification == 'weqd' or self.job_classification == 'heqd':
	# 		self.under_warranty = True
	# 	else:
	# 		self.under_warranty = False

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.job.order') or _('New')

		result = super(AsiaGlobalJobOrder, self).create(vals)
		return result