from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
	_inherit = 'calendar.event'

	type = fields.Selection([
		('new','New'),
		('existing','Existing'),
		('other','Others'),
	], string='Type', default='new')

	partner_id = fields.Many2one('res.partner', string='Customer')
	sale_order_id = fields.Many2one('sale.order', string='Project Reference')
	project_description = fields.Char()

	# def create_lead(self, name):
	# 	new_lead = self.env['crm.lead'].create({
	# 		'name': name,
	# 	})
	# 	result = {
	# 		'type': 'ir.actions.act_window',
	# 		'res_model': 'crm.lead',
	# 		'view_mode': 'form',
	# 		'res_id': new_lead.id,
	# 		'target': 'current',
	# 		'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
	# 	}

	# @api.model
	# def create(self, vals):
	# 	name = vals.get('name')
	# 	super(CalendarEvent, self).create(vals)
	# 	if vals.get('type') == 'new':
	# 		self.create_lead(name)