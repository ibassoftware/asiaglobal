from odoo import models, fields, api, _ 

class JobMaterialRequestForm(models.Model):
	_name = 'asiaglobal.job_material_request_form'
	_description = 'Job / Material Request Form'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', required=True, copy=False, index=True, default=lambda self: _('New'))
	date = fields.Date(default=fields.Datetime.now(), required=True)
	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order', required=True)
	customer_id = fields.Many2one('res.partner', string='Customer', required=True)
	location_id = fields.Many2one('res.partner', string='Location', required=True)
	equipment_id = fields.Many2one('asiaglobal.equipment_profile', required=True)
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
	legacy_no = fields.Char(string="Legacy Number")
	gatepass_dr = fields.Char(string="Gatepass/DR")
	company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.picking'))
	
	total_cost = fields.Float(compute='_compute_total_cost', string='Total JMRF Cost')
	
	@api.depends('line_ids')
	def _compute_total_cost(self):
		for rec in self:
			mycost = 0
			for target_list in rec.line_ids:
				mycost = mycost + target_list.line_cost
				rec.total_cost = mycost

	@api.onchange('jo_id')
	def set_details(self):
		if self.jo_id != False:			
			self.customer_id = self.jo_id.customer_id
			self.location_id = self.jo_id.ship_to.id
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

	stock_picking_id = fields.Many2one('stock.picking', string='Transfer', copy=False)
	
	def create_material_transfer(self):
		for rec in self:
			self.stock_picking_id = self.env['stock.picking'].create({
				'move_type':'direct',
				'picking_type_id': self.picking_id.id,
				'location_id': self.location_id_2.id,
				'location_dest_id': self.destination_id.id,
				'origin': self.name,
				'jmrf_id': self.id,
			}) 

			for target_list in self.line_ids:

				new_id = self.env['stock.move'].create({
					'product_id': target_list.product_id.id,
					'product_uom_qty': target_list.qty,
					'picking_id': self.stock_picking_id.id,
					'name': target_list.product_id.name,
					'product_uom': target_list.product_id.uom_id.id,
					'location_id': self.location_id_2.id,
					'location_dest_id': self.destination_id.id,
					'analytic_account_id': target_list.analytic_account_id.id,
					'analytic_id': target_list.analytic_account_id.id
				})

				target_list.stock_move_id = new_id.id

				new_id.onchange_product_id()

				# child_id = self.stock_picking_id.update({
				# 	'move_lines': [0, 0, {
				# 		'product_id': target_list.product_id,
				# 		'product_uom_qty': target_list.qty,

				# 	}]
				# })


			

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.job.material.request') or _('New')

		result = super(JobMaterialRequestForm, self).create(vals)
		return result

	picking_id = fields.Many2one('stock.picking.type', string='Operation Type')
	location_id_2 = fields.Many2one('stock.location', string='Stock Location')
	destination_id = fields.Many2one('stock.location', string='Destination Location')

class JobMaterialRequestFormLine(models.Model):
	_name = 'asiaglobal.job_material_request_form_line'
	_description = 'Job / Material Request Form Line'

	jmrf_id = fields.Many2one('asiaglobal.job_material_request_form', string='Job Material FRequest Form')
	product_id = fields.Many2one('product.product', string='Product', required=True)
	description = fields.Char()
	part_number = fields.Char()
	qty = fields.Float(required=True)
	item_code = fields.Char()

	stock_move_id = fields.Many2one('stock.move', string='Stock Move')
	line_cost = fields.Float(string='Cost', related='stock_move_id.value')

	analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.", copy=False)

	@api.onchange('product_id')
	def set_product_details(self):
		self.description = self.product_id.description_sale
		self.part_number = self.product_id.default_code