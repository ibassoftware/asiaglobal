from odoo import models, fields, api

class AsiaGlobalMaintenanceJO(models.TransientModel):
	_name = 'asiaglobal.maintenance_jo'

	date = fields.Date()

	def generate(self):
		equipment_ids = self.env['asiaglobal.equipment_profile'].browse(self.env.context.get('active_id'))
		for equipment in equipment_ids:
			equipment.create_maintenance_jo(equipment, self.date)