from odoo import models, fields, api, _ 

class ProductProduct(models.Model):
	_inherit = 'product.product'

	default_code = fields.Char(string='Item Code')
	override_stock_value = fields.Boolean()
	new_stock_value = fields.Float(string='New Stock Value')

	@api.multi
	@api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'product_tmpl_id.cost_method', 'override_stock_value', 'new_stock_value')
	def _compute_stock_value(self):
		for product in self:
			if not product.override_stock_value:
				if product.cost_method in ['standard', 'average']:
					product.stock_value = product.standard_price * product.with_context(company_owned=True).qty_available
				elif product.cost_method == 'fifo':
					product.stock_value = product._sum_remaining_values()
			else:
				product.stock_value = product.new_stock_value

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	default_code = fields.Char(string='Item Code')
	name = fields.Char(string='Product Name/Part/Model Number')