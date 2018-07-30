from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AsiaGlobalServiceReportComplaints(models.Model):
	_name = 'asiaglobal.service_report_complaints'

	service_report = fields.Many2one('asiaglobal.service_report')
	customer_complaint = fields.Text(string='Customer Complaint/s')
	cause = fields.Text()

class AsiaGlobalServiceReportParts(models.Model):
	_name = 'asiaglobal.service_report_parts'

	service_report = fields.Many2one('asiaglobal.service_report')
	product_id = fields.Many2one('product.product', string='Product')
	product_qty = fields.Integer(string='Qty')
	description = fields.Char()
	part_number = fields.Char()

	@api.onchange('product_id')
	def set_product_details(self):
		self.description = self.product_id.name
		self.part_number = self.product_id.code

class AsiaGlobalServiceReport(models.Model):
	_name = 'asiaglobal.service_report'
	_description = 'Service Report'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='SR No.', required=True, copy=False, index=True, default=lambda self: _('New'))
	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order', required=True)

	customer_id = fields.Many2one('res.partner', string='Customer')
	model = fields.Many2one('asiaglobal.manufacturer_model', string='Model')
	# mast_no = fields.Many2one('asiaglobal.mast_type', string='Mast No.')
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
	parts_required = fields.One2many('asiaglobal.service_report_parts', 'service_report')

	with_warranty = fields.Boolean(string='Is the unit within the coverage period?')
	warranty_failure = fields.Boolean(string='if yes, is this a warrantable failure?')
	warranty_failure_reason = fields.Char(string='State Reason')

	billable = fields.Boolean()
	billable_amount = fields.Float(string='Amount')

	technician_id = fields.Many2one('hr.employee', string='Service Technician/s', domain=[('is_technician','=',True)])
	supervisor_id = fields.Many2one('hr.employee', string='Service Supervisor or Manager')

	@api.onchange('technician_id')
	def set_supervisor(self):
		self.supervisor_id = self.technician_id.parent_id

	@api.onchange('jo_id')
	def set_details(self):
		self.customer_id = self.jo_id.customer_id
		self.model = self.jo_id.model
		self.mast_no = self.jo_id.equipment_id.mast_serial_number
		self.serial_number = self.jo_id.serial_number
		self.technician_id = self.jo_id.technician_id

	def update_hour_meter(self, service_hour_meter, jo_id):
		job_order = self.env['asiaglobal.job_order'].search([('id','=',jo_id)])
		equipment = self.env['asiaglobal.equipment_profile'].search([('id','=',job_order.equipment_id.id)])

		equipment_hour_meter = equipment.hour_meter
		new_hour_meter = 0
		if equipment:
			new_hour_meter = equipment_hour_meter + service_hour_meter
		equipment.write({'hour_meter': new_hour_meter})

	@api.model
	def create(self, vals):
		hour_meter = vals.get('hour_meter', False)
		jo_id = vals.get('jo_id', False)
		
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.service.report') or _('New')
		result = super(AsiaGlobalServiceReport, self).create(vals)

		# UPDATE HOUR METER
		if hour_meter and jo_id:
			self.update_hour_meter(hour_meter, jo_id)

		return result

	@api.multi
	def write(self, vals):
		last_hour_meter = self.hour_meter
		new_hour_meter = vals.get('hour_meter', False)
		service_hour_meter = new_hour_meter - last_hour_meter

		jo_id = vals.get('jo_id', False)
		if not jo_id:
			jo_id = self.jo_id.id

		result = super(AsiaGlobalServiceReport, self).write(vals)

		if service_hour_meter and jo_id:
			self.update_hour_meter(service_hour_meter, jo_id)

		return result