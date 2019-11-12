from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class AsiaGlobalJobOrderClassification(models.Model):
	_name = 'asiaglobal.job_order_classification'
	_description = 'Job Order Classification'

	name = fields.Char(string='Job Classification')

class AsiaGlobalJobOrderType(models.Model):
	_name = 'asiaglobal.job_order_type'
	_description = 'Job Order Type'

	name = fields.Char(string='Job Type')

class AsiaGlobalJobOrder(models.Model):
	_name = 'asiaglobal.job_order'
	_description = 'Job Order'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'name desc'

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	initial_complaint = fields.Text()
	customer_id = fields.Many2one('res.partner', string='Customer', required=True)
	ship_to = fields.Many2one('res.partner', string='Ship To / Site Address', required=True)

	type = fields.Selection([
		('admin','ADMIN'),
		('cebu','CEBU'),
		('heqd','HEQD-SERVICE'),
		('heqd_sale','HEQD-SALES'),
		# ('heqd_service','HEQD-SERVICES-DNU'),
		('weqd','WEQD-SERVICE'),
		('weqd_ctd','WEQD-CTD'),
		# ('weqd_rental','WEQD-RENTAL-DNU'),
		('weqd_sale','WEQD-SALES'),
		# ('weqd_service','WEQD-SERVICES-DNU'),
		('rental','WEQD-RENTAL'),
	], string="Department")

	initial_diagnosis = fields.Text()
	technician_id = fields.Many2one('hr.employee', string='Primary Technician', domain=[('is_technician','=',True)])
	ticket_ids = fields.One2many('helpdesk.ticket', 'jo_id', string='Helpdesk Tickets')
	state = fields.Selection([
		('draft','New'),
		('schedule','For Scheduling'),
		('waiting','Waiting for Parts'),
		('progress', 'In Progress'),
		('bill', 'For Billing'),
		('waiting_quote', 'Waiting for Quotation'),
		('waiting_order', 'Waiting for Purchase Order'),
		('done','Done'),
		], string='Status', default='draft', track_visibility='onchange')
	sale_ids = fields.One2many('sale.order', 'jo_id', string='Sale Orders')
	under_warranty = fields.Boolean()
	warranty_date = fields.Date(default=fields.Datetime.now())

	equipment_id = fields.Many2one('asiaglobal.equipment_profile', string='Equipment', required=True)
	manufacturer = fields.Many2one('asiaglobal.manufacturer', string='Manufacturer')
	model = fields.Many2one('asiaglobal.manufacturer_model', string='Model')
	serial_number = fields.Char()
	scheduled_date = fields.Date(default=fields.Datetime.now())
	actual_repair_date = fields.Date(default=fields.Datetime.now())

	service_report_ids = fields.One2many('asiaglobal.service_report', 'jo_id')
	legacy_jo_no = fields.Char(string='Legacy Number')

	# job_classification = fields.Selection([
	# 	('Internal','Internal'),
	# 	('external','External'),
	# 	('warranty','Warranty'),
	# 	('cannibalization','Cannibalization'),
	# ])

	# job_type = fields.Selection([
	# 	('maintenance','Prev Maintenance'),
	# 	('inspection','Diagnostics Inspection'),
	# 	('repair','Repair'),
	# 	('assembly','Assembly/Delivery'),
	# ])

	job_classification = fields.Many2one('asiaglobal.job_order_classification')
	job_type = fields.Many2one('asiaglobal.job_order_type')


	operational = fields.Boolean()
	operational_message = fields.Char(string='Equipment Status', track_visibility='onchange')

	timesheet_ids = fields.One2many('asiaglobal.service_timesheet', 'jo_id')
	job_material_request_ids = fields.One2many('asiaglobal.job_material_request_form', 'jo_id', string="Job / Material Request")

	@api.onchange('operational')
	def set_operational_message(self):
		if self.equipment_id:
			if self.operational == True:
				self.operational_message = "OPERATIONAL"
			else:
				self.operational_message = "NOT OPERATIONAL"

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


	@api.multi
	@api.onchange('customer_id')
	def onchange_customer_id(self):
		if not self.customer_id:
			self.update({
				'ship_to': False,
			})
			return

		addr = self.customer_id.address_get(['delivery'])
		values = {
			'ship_to': addr['delivery'],
		}

		self.update(values)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.job.order') or _('New')

		result = super(AsiaGlobalJobOrder, self).create(vals)
		return result