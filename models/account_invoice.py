from odoo import models, fields, api, _ 
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	delivery_receipt_no = fields.Char(string='Delivery Receipt No.', compute='_get_deliveries')
	bus_style = fields.Char(string='Business Style')
	delivery_receipt_manual_no = fields.Char(string='Delivery Receipt No.')

	@api.multi
	def _get_deliveries(self):
		for record in self:
			delivery_receipt_no = ''
			for invoice in record.invoice_line_ids:
				for sale in invoice.sale_line_ids:
					pickings = sale.mapped('order_id').mapped('picking_ids')
					for pick in pickings:
						if pick.state not in ['draft','cancel']:
							if not delivery_receipt_no:
								delivery_receipt_no = pick.name
							else:
								delivery_receipt_no += ', %s' % pick.name
			record.delivery_receipt_no = delivery_receipt_no

class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	@api.multi
	def _get_description(self):
		for record in self:
			description_name = ''
			if record.name:
				description_name = record.name.replace('\n', ' ')
			record.description_name = description_name

	# EXTEND TO USE CUSTOM SALES DECIMAL ACCURACY
	price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))
	description_name = fields.Text(compute='_get_description')
