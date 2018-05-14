# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class AsiaglobalPartner(models.Model):
	_inherit = 'res.partner'

	is_principal = fields.Boolean(
		string='Is Principal',
	)

	first_name = fields.Char()
	last_name = fields.Char()

	# @api.onchange('first_name')
	# def set_first_name(self):
	# 	name = self.name
	# 	if self.first_name:
	# 		name = self.first_name
	# 	if self.first_name and self.last_name:
	# 		name = self.first_name + ' ' + self.last_name 
	# 	self.name = name

	# @api.onchange('last_name')
	# def set_last_name(self):
	# 	name = self.name
	# 	if self.last_name:
	# 		name = self.last_name
	# 	if self.first_name and self.last_name:
	# 		name = self.first_name + ' ' + self.last_name 
	# 	self.name = name

# class AsiaglobalLead(models.Model):
# 	_inherit = 'crm.lead'

# 	principal_id = fields.Many2one(
# 		'res.partner',
# 		string='Principal',
# 		domain=[('is_principal','=',True), ]
# 	)

# 	opportunity_type = fields.Selection([('Indent', 'Indent'), ('forward', 'Forward Sale'), ('other', 'Other')],
# 		default= "forward")

# 	expected_gross_margin = fields.Float(
# 		string='Expected Gross Margin (%)',
# 	)

# 	gross_margin_value = fields.Float(
# 		string='Margin in value',
# 		compute='_compute_margin',
# 		store=True,
# 	)

# 	legacy_quote = fields.Char(
# 		string='Legacy Sales Quote Number',
# 	)

# 	sale_type = fields.Selection([('unit', 'Unit Sales'), ('parts', 'Parts Sales'), ('others', 'Others')],
# 		default= "unit")

# 	@api.depends('gross_margin_value', 'expected_gross_margin', 'planned_revenue')
# 	def _compute_margin(self):
# 		for rec in self:
# 			rec.gross_margin_value = rec.planned_revenue * (rec.expected_gross_margin * 0.01)

# 	@api.model
# 	def create(self, values):
# 		record = super(AsiaglobalLead, self).create(values)
# 		try:
# 			employee = self.env['hr.employee'].search([('user_id','=',record['user_id'].id)])[0]
# 			if employee:

# 				employee_manager = employee.parent_id.id
# 				_logger.info('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# 				_logger.info(employee.name)
# 				_logger.info(employee.parent_id.name)
# 				_logger.info(employee.parent_id.user_id.partner_id.id)

# 				if employee_manager:
# 					record.message_subscribe([employee.parent_id.user_id.partner_id.id])
# 		except Exception as e:
# 			pass
		
# 		return record

	

# 	@api.one
# 	@api.constrains('planned_revenue', 'expected_gross_margin')
# 	def _check_minimum(self):
# 		if self.type == 'opportunity':
# 			if self.planned_revenue <= 0 or self.expected_gross_margin <= 0:
# 				raise ValidationError("Revenue and Gross Margin must be more than zero")

# 	@api.depends('order_ids')
# 	def _compute_sale_amount_total(self):
# 		for lead in self:
# 			total = 0.0
# 			nbr = 0
# 			company_currency = lead.company_currency or self.env.user.company_id.currency_id
# 			for order in lead.order_ids:
# 				if order.state in ('draft', 'sent', 'sale','manager_approval', 'admin_approval', 'approved'):
# 					nbr += 1
# 				if order.state not in ('draft', 'sent', 'cancel', 'manager_approval', 'admin_approval', 'approved'):
# 					total += order.currency_id.compute(order.amount_untaxed, company_currency)
# 			lead.sale_amount_total = total
# 			lead.sale_number = nbr

		# if employee:
		# 	employee_manager = employee.parent_id.id
		# 	if employee_manager:
		# 		self.message_subscribe([employee_manager])
		# return record

class AGSQStages(models.Model):
	_name = 'asiaglobal.stages'
	name = fields.Char(
		string='Stage Name',
		size=64,
		required=True
		)
	probability = fields.Float(
		string='Probability in %',
	)


	
class AGSaleOrder(models.Model):
	_inherit = 'sale.order'

	subject = fields.Text()
	notes = fields.Text(help='Notes')

	state = fields.Selection([
		('draft', 'For Approval'),
		('manager_approval', 'Manager Approval'),
		('admin_approval', 'CEO Approval'),
		('approved', 'Approved'),
		('sent', 'Quotation Sent'),
		('sale', 'Sales Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	principal_id = fields.Many2one(
		'res.partner',
		string='Principal',
		domain=[('is_principal','=',True), ]
	)

	opportunity_type = fields.Selection([('Indent', 'Indent'), ('forward', 'Forward Sale'), ('other', 'Other')],
		default= "forward")

	expected_gross_margin = fields.Float(
		string='Expected Gross Margin (%)',
	)

	legacy_quote = fields.Char(
		string='Legacy Sales Quote Number',
	)

	sale_type = fields.Selection([('unit', 'Unit Sales'), ('parts', 'Parts Sales'), ('others', 'Others')],
		default= "unit")

	project_stage_id = fields.Many2one(
		'asiaglobal.stages',
		string='Project Stage',
		track_visibility='onchange',
	)

	project_probability = fields.Float(
		string='Probability %',
		compute= '_compute_probability',
		store=True,
	)

	exchange_rate = fields.Float(
		string='Exchange Rate (Sales Only)',
	)

	current_currency = fields.Char(
		string='Currency',
		compute='_get_currency'
	)

	@api.depends('pricelist_id')
	def _get_currency(self):
		self.current_currency = self.pricelist_id.currency_id.name


	@api.depends('project_stage_id')
	@api.one
	def _compute_probability(self):
		if (self.project_stage_id):
			self.project_probability = self.project_stage_id.probability

	expected_gross_value = fields.Float(
		string='Amount in PHP Net of VAT',
		compute= '_compute_gross_value',
		store=True,
	)

	@api.depends('pricelist_id', 'expected_gross_margin', 'exchange_rate', 'amount_total')
	@api.one
	def _compute_gross_value(self):
		if self.current_currency != 'PHP':
			self.expected_gross_value = self.amount_total * self.exchange_rate
		else:
			self.expected_gross_value = self.amount_total

	gross_margin_value = fields.Float(
		string='Estimated Gross Margin in PHP',
		compute='_compute_gross_margin',
		store=True
	)

	@api.depends('expected_gross_value', 'expected_gross_margin')
	@api.one
	def _compute_gross_margin(self):
		self.gross_margin_value = self.expected_gross_value * (self.expected_gross_margin * .01)


	project_description = fields.Char(
		string='Project Description',
		required=True,
	)


	def manager_approval(self):
		if (self.team_id.name == "HEQD" and self.sale_type == "unit"
		and self.opportunity_type == "forward" ):
			if ( self.expected_gross_value <= 5000000 and self.expected_gross_margin >= 18 ):
				self.state = "approved"
				return
			
		if (self.team_id.name == "HEQD" and self.sale_type == "unit"
		and self.opportunity_type == "Indent" ):
			if ( self.expected_gross_value <= 5000000 and self.expected_gross_margin >= 12 ):
				self.state = "approved"
				return
			
		if (self.team_id.name == "HEQD" and self.sale_type == "parts"):
			if ( self.expected_gross_value <= 500000 and self.expected_gross_margin >= 25 ):
				self.state = "approved"
				return

		if (self.team_id.name == "WEQD" and self.sale_type == "unit"
		and self.opportunity_type == "forward" ):
			if ( self.expected_gross_value <= 3000000 and self.expected_gross_margin >= 18 ):
				self.state = "approved"
				return
			
		if (self.team_id.name == "WEQD" and self.sale_type == "unit"
		and self.opportunity_type == "Indent" ):
			if ( self.expected_gross_value <= 3000000 and self.expected_gross_margin >= 12 ):
				self.state = "approved"
				return
			
		if (self.team_id.name == "WEQD" and self.sale_type == "parts"):
			if ( self.expected_gross_value <= 500000 and self.expected_gross_margin >= 25 ):
				self.state = "approved"
				return

		if (self.team_id.name == "Rentals" and self.sale_type == "parts"):
			if ( self.expected_gross_value <= 500000):
				self.state = "approved"
				return
		
		
		self.state = "admin_approval"
		return

	def admin_approval(self):
		self.state = "approved"	

	attention_to = fields.Char(
	    string='Attention To',
	)

	note_to_customer = fields.Text(
	    string='Note To Customer',
	)

	approving_manager_id = fields.Many2one(
	    'hr.employee',
	    string='Approving Manager',
	)

	# @api.multi
	# def write(self, vals):
	# 	res = super(AGSaleOrder, self).write(vals)
	# 	_logger.info('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
	# 	if (self.state == 'sale'):
	# 		won= self.env['asiaglobal.stages'].search([('name','=','Won')],limit=1).id
	# 		_logger.info(won)
	# 		vals['project_stage_id'] = won

	# 	res = super(AGSaleOrder, self).write(vals)
	# 		self.project_stage_id = won

	# 	return res


# class asiaglobal(models.Model):
#     _name = 'asiaglobal.asiaglobal'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100