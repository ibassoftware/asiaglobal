# from odoo import models, fields, api, _ 

# class PurchaseOrder(models.Model):
# 	_inherit = 'purchase.order'

# 	department = fields.Char(compute='_get_analytic_tags')

# 	@api.multi
# 	def _get_analytic_tags(self):
# 		for order in self:
# 			tag_ids = order.mapped('order_line').mapped('analytic_tag_ids')[0]
# 			order.department = tag_ids.name