from odoo import models, fields, api, _ 

# from collections import defaultdict

class StockMove(models.Model):
	_inherit = 'stock.move'

	product_id_code = fields.Char(string='Item Code', compute='_get_product_details')
	product_id_partno =  fields.Char(string='Part Number', compute='_get_product_details')
	product_id_description = fields.Char(string='Description', compute='_get_product_details')
	location = fields.Char()

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