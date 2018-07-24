from odoo import models, fields, api, _ 

class HelpdeskTicket(models.Model):
	_inherit = 'helpdesk.ticket'

	jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')