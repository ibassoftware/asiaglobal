# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import re
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext


class AsiaglobalPartner(models.Model):
	_inherit = 'res.partner'

	is_principal = fields.Boolean(
		string='Is Principal',
	)

	first_name = fields.Char()
	last_name = fields.Char()

class AGTSalesActivity(models.Model):
	_inherit = 'mail.activity'

	sale_order_id = fields.Many2one(
		'sale.order',
		string='Project Reference',
		compute="_get_order_reference"
	)

	partner_id = fields.Many2one(
		'res.partner',
		string='Customer',
		compute="_resolve_other_data"
	)

	principal_id = fields.Many2one(
		'res.partner',
		string='Principal',
		compute="_resolve_other_data"
	)

	team_id = fields.Many2one(
		'crm.team',
		string='Sales Channel',
		compute="_resolve_other_data"
	)

	project_description = fields.Char(
		string='Project',
		compute="_resolve_other_data"
	)

	
	@api.depends('res_name','res_model_id')
	@api.one
	def _get_order_reference(self):
		if (self.res_model_id.model == 'sale.order'):
			ref_sale_id = self.env['sale.order'].search([('name', '=',self.res_name)], limit=1)
			self.sale_order_id = ref_sale_id
			return ref_sale_id

	@api.depends('sale_order_id')
	@api.one
	def _resolve_other_data(self):
		self.partner_id = self.sale_order_id.partner_id
		self.principal_id = self.sale_order_id.principal_id
		self.team_id = self.sale_order_id.team_id
		self.project_description =self.sale_order_id.project_description

	@api.multi
	def action_done(self):
		""" Wrapper without feedback because web button add context as
		parameter, therefore setting context to feedback """
		return self.action_feedback()

	def action_feedback(self, feedback=False):
		message = self.env['mail.message']
		if feedback:
			self.write(dict(feedback=feedback))
		for activity in self:
			record = self.env[activity.res_model].browse(activity.res_id)
			record.message_post_with_view(
				'mail.message_activity_done',
				values={'activity': activity},
				subtype_id=self.env.ref('mail.mt_activities').id,
				mail_activity_type_id=activity.activity_type_id.id,
			)
			message |= record.message_ids[0]

		# Add handling here
		feedback_message = ""
		if self.feedback:
			feedback_message = cleanhtml(self.feedback)
		if (self.res_model_id.model == 'sale.order'):
			self.env['asiaglobal.sales_report'].create({
				'sale_order_id':self.sale_order_id.id,
				'partner_id': self.partner_id.id,
				'principal_id': self.principal_id.id,
				'team_id': self.sale_order_id.team_id.id,
				'project_description': self.project_description,
				'activity_summary': self.summary,
				'feedback': feedback_message,
				'user_id': self.env.uid
				})
		self.unlink()
		return message.ids and message.ids[0] or False

class AGTSalesReports(models.Model):
	_name = 'asiaglobal.sales_report'
	
	sale_order_id = fields.Many2one(
		'sale.order',
		string='Project Reference',
	)

	partner_id = fields.Many2one(
		'res.partner',
		string='Customer',
	)

	principal_id = fields.Many2one(
		'res.partner',
		string='Principal',
	)

	team_id = fields.Many2one(
		'crm.team',
		string='Sales Channel',
	)

	project_description = fields.Char(
		string='Project',
		
	)

	activity_summary = fields.Char(
		string='Activity Summary',
	)

	feedback = fields.Char(
		string='Feedback',
	)

	user_id = fields.Many2one(
	    'res.users',
	    string='Employee',
	)

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

	opportunity_type = fields.Selection([
		('Indent', 'Indent'), 
		('forward', 'Forward Sale'), 
		('part', 'Part Sales'),
		('service', 'Service'),
		('other', 'Other'),
		], default= "forward")

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
	@api.one
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

		if (self.opportunity_type == "forward"):
			if (self.expected_gross_value <= self.team_id.maximum_gross_value_forward and self.expected_gross_margin >= self.team_id.minimum_gross_margin_forward):
				self.state = "approved"
				return

		if (self.opportunity_type == "Indent"):
			if (self.expected_gross_value <= self.team_id.maximum_gross_value and self.expected_gross_margin >= self.team_id.minimum_gross_margin):
				self.state = "approved"
				return

		if (self.opportunity_type == "part"):
			if (self.expected_gross_value <= self.team_id.maximum_gross_value_part and self.expected_gross_margin >= self.team_id.minimum_gross_margin_part):
				self.state = "approved"
				return

		if (self.opportunity_type == "service"):
			if (self.expected_gross_value <= self.team_id.maximum_gross_value_service and self.expected_gross_margin >= self.team_id.minimum_gross_margin_service):
				self.state = "approved"
				return
		

		# if (self.team_id.name == "HEQD" and self.sale_type == "unit"
		# and self.opportunity_type == "forward" ):
		# 	if ( self.expected_gross_value <= 5000000 and self.expected_gross_margin >= 18 ):
		# 		self.state = "approved"
		# 		return
			
		# if (self.team_id.name == "HEQD" and self.sale_type == "unit"
		# and self.opportunity_type == "Indent" ):
		# 	if ( self.expected_gross_value <= 5000000 and self.expected_gross_margin >= 12 ):
		# 		self.state = "approved"
		# 		return
			
		# if (self.team_id.name == "HEQD" and self.sale_type == "parts"):
		# 	if ( self.expected_gross_value <= 500000 and self.expected_gross_margin >= 25 ):
		# 		self.state = "approved"
		# 		return

		# if (self.team_id.name == "WEQD" and self.sale_type == "unit"
		# and self.opportunity_type == "forward" ):
		# 	if ( self.expected_gross_value <= 3000000 and self.expected_gross_margin >= 18 ):
		# 		self.state = "approved"
		# 		return
			
		# if (self.team_id.name == "WEQD" and self.sale_type == "unit"
		# and self.opportunity_type == "Indent" ):
		# 	if ( self.expected_gross_value <= 3000000 and self.expected_gross_margin >= 12 ):
		# 		self.state = "approved"
		# 		return
			
		# if (self.team_id.name == "WEQD" and self.sale_type == "parts"):
		# 	if ( self.expected_gross_value <= 500000 and self.expected_gross_margin >= 25 ):
		# 		self.state = "approved"
		# 		return

		# if (self.team_id.name == "Rentals" and self.sale_type == "parts"):
		# 	if ( self.expected_gross_value <= 500000):
		# 		self.state = "approved"
		# 		return
		
		
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

class AGTSaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	prod_categ_id = fields.Many2one(
	    'product.category',
	    string='Category',
	)

	# EXTEND TO USE CUSTOM SALES DECIMAL ACCURACY
	price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))

	