from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp

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

	@api.onchange('product_id')
	def onchange_product_id(self):
        
		result = {}
		if not self.product_id:
			return result

		# Reset date, price and quantity since _onchange_quantity will provide default values
		self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
		self.price_unit = self.product_qty = 0.0
		self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
		result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

		product_lang = self.product_id.with_context(
			lang=self.partner_id.lang,
			partner_id=self.partner_id.id,
		)
		# self.name = product_lang.display_name
		# if product_lang.description_purchase:
		#     self.name += '\n' + product_lang.description_purchase

		self.part_number = self.product_id.name
		self.name = self.product_id.description_purchase

		fpos = self.order_id.fiscal_position_id
		if self.env.uid == SUPERUSER_ID:
			company_id = self.env.user.company_id.id
			self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
		else:
			self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

		self._suggest_quantity()
		self._onchange_quantity()

		

		return result
		
			