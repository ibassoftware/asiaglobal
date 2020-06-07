from odoo import models, fields, api, _ 

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	location = fields.Char()
	remarks = fields.Text()
	validated_by = fields.Many2one('res.users')

	payment_terms = fields.Char(string='Payment Terms', compute='_get_invoice_details')
	invoice_no = fields.Char(string='Invoice No.', compute='_get_invoice_details')
	purchase_no = fields.Char(string='P.O No.', compute='_get_invoice_details')
	jmrf_id = fields.Many2one('asiaglobal.job_material_request_form', string="Job / Material Request Form", copy=False)

	@api.multi
	def button_validate(self):
		result = super(StockPicking, self).button_validate()
		for pick in self:
			pick.validated_by = self.env.user
		return result

	@api.multi
	def _get_invoice_details(self):
		# payment_terms = ''
		# invoice_no = ''
		# purchase_no = ''
		for record in self:
			order_id = record.mapped('move_lines').mapped('sale_line_id').mapped('order_id')
			purchase_no = order_id.client_order_ref
			payment_terms = ""
			invoice_no = ""

			move_lines = record.mapped('move_lines')
			
			for move in move_lines:
				invoice_lines = move.mapped('sale_line_id').mapped('invoice_lines')
				for line in invoice_lines:
					if move.product_id == line.product_id:
						payment_terms = line.invoice_id.payment_term_id.name
						invoice_no = line.invoice_id.number
			
			record.payment_terms = payment_terms
			record.invoice_no = invoice_no
			record.purchase_no = purchase_no
