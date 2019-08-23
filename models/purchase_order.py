from odoo import models, fields, api, _ 

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	department = fields.Char(compute='_get_analytic_tags')
	ship_via = fields.Char(string='Ship Via')

	@api.multi
	def _get_analytic_tags(self):
		for order in self:
			department = ''
			tag_ids = order.mapped('order_line').mapped('analytic_tag_ids')
			for tag in tag_ids:
				if department:
					department += ', '
					department += tag.name
				else:
					department = tag.name
			order.department = department

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	part_number = fields.Char()