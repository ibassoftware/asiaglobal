from odoo import models, fields, api, _ 

class StockMove(models.Model):
	_inherit = 'stock.move'

	product_id_code = fields.Char(string='Item Code', compute='_get_product_details')
	product_id_partno =  fields.Char(string='Part Number', compute='_get_product_details')
	product_id_description = fields.Char(string='Description', compute='_get_product_details')

	@api.multi
	@api.depends('product_id')
	def _get_product_details(self):
		for record in self:
			record.product_id_code = record.product_id.default_code
			record.product_id_partno = record.product_id.name
			record.product_id_description = record.product_id.description_sale