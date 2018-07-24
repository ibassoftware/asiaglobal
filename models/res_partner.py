from odoo import models, fields, api, _ 

class ResPartner(models.Model):
	_inherit = 'res.partner'

	equipment_ids = fields.One2many('asiaglobal.equipment_profile','customer', string='Equipments')