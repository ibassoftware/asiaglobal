from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	def _get_default_user(self):
		return self.env.user

	department = fields.Char(compute='_get_analytic_tags')
	ship_via = fields.Char(string='Ship Via')
	prepared_by = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=_get_default_user)

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

	# NEW FIELDS
	part_number = fields.Char()

	# OVERRIDE
	price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))

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

	@api.multi
	def _prepare_stock_moves(self, picking):
		result = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
		if result and self.account_analytic_id:
			# result[0]['analytic_account_id'] = self.account_analytic_id.id
			result[0].update({'analytic_account_id': self.account_analytic_id.id})
		return result
			