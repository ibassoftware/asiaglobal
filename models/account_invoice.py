from odoo import models, fields, api, _ 

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	delivery_receipt_no = fields.Char(string='Delivery Receipt No.', compute='_get_deliveries')

	@api.multi
	def _get_deliveries(self):
		delivery_receipt_no = ''
		for invoice in self.invoice_line_ids:
			for sale in invoice.sale_line_ids:
				pickings = sale.mapped('order_id').mapped('picking_ids')
				for pick in pickings:
					delivery_receipt_no += '%s ,' % pick.name

