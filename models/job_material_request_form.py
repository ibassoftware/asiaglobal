from odoo import models, fields, api, _ 

class JobMaterialRequestForm(models.Model):
	_name = 'asiaglobal.job_material_request_form'
	_description = 'Job / Material Request Form'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', required=True, copy=False, index=True, default=lambda self: _('New'))
	date = fields.Date(default=fields.Datetime.now())
	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')
	customer_id = fields.Many2one('res.partner', string='Customer')
	location_id = fields.Many2one('res.partner', string='Location')
	equipment_id = fields.Many2one('asiaglobal.equipment_profile')
	model = fields.Many2one('asiaglobal.manufacturer_model')
	serial_number = fields.Char()
	hour_meter = fields.Float()
	is_warranty = fields.Boolean(string='Warranty')
	is_rental = fields.Boolean(string='Rental')
	is_operational = fields.Boolean(string='Operational')
	is_not_operational = fields.Boolean(string='Not Operational')
	is_urgent = fields.Boolean(string='Urgent')
	line_ids = fields.One2many('asiaglobal.job_material_request_form_line', 'jmrf_id')
	remarks = fields.Text()
	request_by = fields.Many2one('res.users')
	noted_by = fields.Many2one('res.users')
	approved_by = fields.Many2one('res.users')

	@api.onchange('jo_id')
	def set_details(self):
		self.customer_id = self.jo_id.customer_id
		self.location_id = self.jo_id.ship_to
		self.equipment_id = self.jo_id.equipment_id
		self.model = self.jo_id.model
		self.serial_number = self.jo_id.serial_number
		# self.operational = self.jo_id.equipment_id.operational
		if self.jo_id.under_warranty == True:
			self.is_warranty = True
		else:
			self.is_warranty = False

	@api.onchange('equipment_id')
	def set_equipment_details(self):
		if self.equipment_id:
			self.model = self.equipment_id.model
			self.serial_number = self.equipment_id.serial_number
			self.hour_meter = self.equipment_id.hour_meter
			if self.equipment_id.operational == True:
				self.operational = True
				self.is_not_operational = False
			else:
				self.operational = False
				self.is_not_operational = True			

	@api.multi
	@api.onchange('customer_id')
	def onchange_customer_id(self):
		if not self.customer_id:
			self.update({
				'location_id': False,
			})
			return

		addr = self.customer_id.address_get(['delivery'])
		values = {
			'location_id': addr['delivery'],
		}

		self.update(values)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.job.material.request') or _('New')

		result = super(JobMaterialRequestForm, self).create(vals)
		return result

class JobMaterialRequestFormLine(models.Model):
	_name = 'asiaglobal.job_material_request_form_line'
	_description = 'Job / Material Request Form Line'

	jmrf_id = fields.Many2one('asiaglobal.job_material_request_form', string='Job Material FRequest Form')
	product_id = fields.Many2one('product.product', string='Product')
	description = fields.Char()
	part_number = fields.Char()
	qty = fields.Float()
	item_code = fields.Char()

	@api.onchange('product_id')
	def set_product_details(self):
		self.description = self.product_id.description_sale
		self.part_number = self.product_id.default_code