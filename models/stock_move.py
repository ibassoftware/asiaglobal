from odoo import models, fields, api, _ 

# from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
	_inherit = 'stock.move'

	@api.multi
	def _get_landed_cost(self):
		for record in self:
			has_landed_cost = False
			move_ids = self.env['stock.move'].search([('product_id','=',record.product_id.id),('state','=','done'),('remaining_qty','>',0)])
			for move in move_ids:
				if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
					landed_cost_line = self.env['stock.valuation.adjustment.lines'].search([('move_id','=',move.id)])
					for line in landed_cost_line:
						if line.cost_id.state in ['validate','done']:
							has_landed_cost = True
			record.has_landed_cost = has_landed_cost

	product_id_code = fields.Char(string='Item Code', compute='_get_product_details')
	product_id_partno =  fields.Char(string='Part Number', compute='_get_product_details')
	product_id_description = fields.Char(string='Description', compute='_get_product_details')
	location = fields.Char()
	has_landed_cost = fields.Boolean(string='With LC?', compute="_get_landed_cost")

	@api.multi
	@api.depends('product_id')
	def _get_product_details(self):
		for record in self:
			record.product_id_code = record.product_id.default_code
			record.product_id_partno = record.product_id.name
			record.product_id_description = record.product_id.description_sale

	@api.multi
	def move_account_entry_move(self):
		for move in self:
			if not move.account_move_ids and move.value != 0:
				move.with_context(force_period_date=move.date)._account_entry_move()

class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	value = fields.Float(related="move_id.value", copy=False)
	remaining_qty = fields.Float(related="move_id.remaining_qty", copy=False)
	remaining_value = fields.Float(related="move_id.remaining_value", copy=False)
	price_unit = fields.Float(related="move_id.price_unit", string='Unit Price', copy=False)