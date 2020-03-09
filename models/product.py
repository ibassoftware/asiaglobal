# # -*- RCS -*-
from odoo import models, fields, api, _ 

class ProductProduct(models.Model):
	_inherit = 'product.product'

	default_code = fields.Char(string='Item Code')
	override_stock_value = fields.Boolean()
	new_stock_value = fields.Float(string='New Stock Value')

	@api.multi
	@api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'product_tmpl_id.cost_method', 'override_stock_value', 'new_stock_value')
	def _compute_stock_value(self):
		result = super(ProductProduct, self)._compute_stock_value()
		for product in self:
			if product.override_stock_value:
				product.stock_value = product.new_stock_value
		return result

	@api.multi
	def compute_stock_value(self):
		for product in self:
			product._compute_stock_value()

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	default_code = fields.Char(string='Item Code')
	name = fields.Char(string='Product Name/Part/Model Number')