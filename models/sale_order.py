from odoo import models, fields, api, _ 

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