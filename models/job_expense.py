from odoo import models, fields, api, _ 

class JobExpense(models.Model):
	_name = 'asiaglobal.job_expense'
	_description = 'Job Expense'

	@api.depends('qty', 'amount')
	def _compute_amount(self):
		"""
		Compute the amounts of the expense
		"""
		for line in self:
			amount_total = line.amount * line.qty
			line.update({
				'amount_total': amount_total
			})

	description = fields.Char(required=True)
	qty = fields.Float()
	amount = fields.Float()
	amount_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)
	supplier_name = fields.Many2one('res.partner', domain=[('supplier','=',True)])
	equipment_id = fields.Many2one('asiaglobal.equipment_profile', string='Equipment', required=True)
	po_id = fields.Many2one('purchase.order', string='AGT PO #')