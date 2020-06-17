from odoo import models, fields, api, _ 
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# NEW FIELDS
	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')
	sale_source = fields.Selection([
		('exhibit', 'Exhibit'),
		('new', 'New Client'),
		('referral', 'Referral'),
		('saturation', 'Saturation'),
		('old', 'Old Customer'),
		('other', 'Others'),
	], string='Source of Sale')

	# OVERRIDE
	validity_date = fields.Date(states={'draft': [('readonly', False)], 'manager_approval': [('readonly', False)], 'admin_approval': [('readonly', False)], 'approved': [('readonly', False)], 'sent': [('readonly', False)]},)

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		result = super(SaleOrderLine, self).product_id_change()
		vals = {}
		product = self.product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=self.product_uom.id
		)
		name = product.default_code or ''
		if product.description_sale:
			name += '\n' + product.description_sale
		# If no description and item code
		if not name:
			name = product.name
		vals['name'] = name
		self.update(vals)
		return result
