from odoo import models, fields, api, _ 

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	is_technician = fields.Boolean(string='Technician')