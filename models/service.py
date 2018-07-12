from odoo import models, fields, api
import logging
import re
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class AGTEquipments(models.Model):
	_name = 'asiaglobal.equipments'

	model_id = fields.Many2one(
		'asiaglobal.equipment_models',
		string='Equipment Model',
	)

	principal_id = fields.Many2one(
	    'asiaglobal.equipmentprincipal',
	    string='Principal',
	)

	serial_number = fields.Char(
	    string='Serial Number',
	    _sql_constraints = [
         ('unique_serial', 'unique (your_field_name)','Serial Number must be unique!')]
	)

	date_of_delivery = fields.Date(
	    string='Date of Delivery'
	)

	sold_by = fields.Char(
	    string='Sold By',
	)

	

class AGTEquipmentModels(models.Model):
	_name = 'asiaglobal.equipment_models'

	name = fields.Char(
		string='Model',
		size=64,
		required=False,
		readonly=False,
		defaults={:False}
		)

	principal_id = fields.Many2one(
		'asiaglobal.equipmentprincipal',
		string='Principal',
	)

class AGTEquipmentPrincipal(models.Model):
	_name = 'asiaglobal.equipmentprincipal'

	name = fields.Char(
		string='',
		size=64,
		required=False,
		readonly=False,
		defaults={:False}
		)