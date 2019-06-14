from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AsiaGlobalServiceReportComplaints(models.Model):
	_name = 'asiaglobal.service_report_complaints'

	service_report = fields.Many2one('asiaglobal.service_report')
	name = fields.Text(string='Customer Complaint/s', required=True, oldname='customer_complaint')
	cause = fields.Text()

class AsiaGlobalServiceReportParts(models.Model):
	_name = 'asiaglobal.service_report_parts'
	_description = 'Parts Fitted'

	service_report = fields.Many2one('asiaglobal.service_report')
	product_id = fields.Many2one('product.product', string='Product')
	product_qty = fields.Integer(string='Qty')
	description = fields.Char()
	part_number = fields.Char()
	amount = fields.Float(string='Amount (Cost)')

	@api.onchange('product_id')
	def set_product_details(self):
		self.description = self.product_id.description_sale
		self.part_number = self.product_id.default_code
		self.amount = self.product_id.standard_price

class AsiaGlobalServiceReportPartsRequired(models.Model):
	_name = 'asiaglobal.service_report_parts_required'
	_description = 'Parts Required'

	service_report = fields.Many2one('asiaglobal.service_report')
	product_id = fields.Many2one('product.product', string='Product')
	product_qty = fields.Integer(string='Qty')
	description = fields.Char()
	part_number = fields.Char()
	amount = fields.Float(string='Amount (Cost)')

	@api.onchange('product_id')
	def set_product_details(self):
		self.description = self.product_id.description_sale
		self.part_number = self.product_id.default_code
		self.amount = self.product_id.standard_price

class AsiaGlobalServiceReport(models.Model):
	_name = 'asiaglobal.service_report'
	_description = 'Service Report'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='SR No.', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order', required=True)

	customer_id = fields.Many2one('res.partner', string='Customer')
	ship_to = fields.Many2one('res.partner', string='Ship To / Site Address')
	equipment_id = fields.Many2one('asiaglobal.equipment_profile', string='Equipment')
	model = fields.Many2one('asiaglobal.manufacturer_model', string='Model')
	mast_no = fields.Char(string='Mast No.')
	serial_number = fields.Char(string='Truck Serial No.')
	hour_meter = fields.Float()

	visit_date = fields.Date(string='Date of Visit', default=fields.Datetime.now(), required=True)
	time_in = fields.Float()
	time_out = fields.Float()

	customer_complaints = fields.One2many('asiaglobal.service_report_complaints', 'service_report')
	service_rendered = fields.Text()
	recommendation = fields.Text(string='Recommendation / Remarks')

	is_parts_fitted = fields.Boolean()
	parts_fitted = fields.One2many('asiaglobal.service_report_parts', 'service_report')
	is_parts_required = fields.Boolean()
	parts_required = fields.One2many('asiaglobal.service_report_parts_required', 'service_report')

	with_warranty = fields.Boolean(string='Is the unit within the coverage period?')
	warranty_failure = fields.Boolean(string='if yes, is this a warrantable failure?')
	warranty_failure_reason = fields.Char(string='State Reason')

	billable = fields.Boolean()
	billable_amount = fields.Float(string='Amount')

	technician_id = fields.Many2one('hr.employee', string='Service Technician', domain=[('is_technician','=',True)])
	technician_ids = fields.Many2many('hr.employee', string='Other Technicians', domain=[('is_technician','=',True)])
	supervisor_id = fields.Many2one('hr.employee', string='Service Supervisor or Manager')

	legacy_service_report_no = fields.Char(string='Legacy Service Report #')

	operational = fields.Boolean()
	operational_message = fields.Char(string='Equipment Status', track_visibility='onchange')

	@api.onchange('operational')
	def set_operational_message(self):
		if self.jo_id:
			if self.operational == True:
				self.operational_message = "OPERATIONAL"
			else:
				self.operational_message = "NOT OPERATIONAL"

	@api.onchange('technician_id')
	def set_supervisor(self):
		self.supervisor_id = self.technician_id.parent_id

	@api.onchange('jo_id')
	def set_details(self):
		self.customer_id = self.jo_id.customer_id
		self.ship_to = self.jo_id.ship_to
		self.equipment_id = self.jo_id.equipment_id
		self.model = self.jo_id.model
		self.mast_no = self.jo_id.equipment_id.mast_serial_number
		self.serial_number = self.jo_id.serial_number
		self.technician_id = self.jo_id.technician_id
		self.operational = self.jo_id.equipment_id.operational

	def update_operational(self, operational, jo_id, operational_message):
		job_order = self.env['asiaglobal.job_order'].search([('id','=',jo_id)])
		equipment = self.env['asiaglobal.equipment_profile'].search([('id','=',job_order.equipment_id.id)])

		job_order.write({'operational': operational, 'operational_message': operational_message})
		equipment.write({'operational': operational, 'operational_message': operational_message})

	@api.model
	def create(self, vals):
		jo_id = vals.get('jo_id', False)
		operational = vals.get('operational')
		operational_message = vals.get('operational_message')
		
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.service.report') or _('New')
		result = super(AsiaGlobalServiceReport, self).create(vals)

		self.update_operational(operational, jo_id, operational_message)

		return result

	@api.multi
	def write(self, vals):
		operational = vals.get('operational')
		operational_message = vals.get('operational_message')

		jo_id = vals.get('jo_id', False)
		if not jo_id:
			jo_id = self.jo_id.id

		result = super(AsiaGlobalServiceReport, self).write(vals)

		self.update_operational(operational, jo_id, operational_message)

		return result