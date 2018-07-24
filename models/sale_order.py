from odoo import models, fields, api, _ 

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')