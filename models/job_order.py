from odoo import models, fields, api, _ 

class AsiaGlobalJobOrder(models.Model):
	_name = 'asiaglobal.job_order'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	initial_complaint = fields.Text()
	customer_id = fields.Many2one('res.partner', string='Customer')
	type = fields.Selection([
		('proactive','Proactive'),
		('reactive','Reactive')
	])
	initial_diagnosis = fields.Text()
	# technician_id = fields.Many2many('hr.employee', string='Technicians Assigned', domain=[('is_technician','=',True)])
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

	@api.onchange('equipment_id')
	def set_equipment_details(self):
		self.manufacturer = self.equipment_id.manufacturer
		self.model = self.equipment_id.model
		self.serial_number = self.equipment_id.serial_number

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('asiaglobal.job.order') or _('New')

		result = super(AsiaGlobalJobOrder, self).create(vals)
		return result