# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AsiaGlobalEquipmentType(models.Model):
	_name = 'asiaglobal.equipment_type'

	name = fields.Char(required=True)

class AsiaGlobalEngineModel(models.Model):
	_name = 'asiaglobal.engine_model'

	name = fields.Char(required=True)
	manufacturer = fields.Many2one('asiaglobal.manufacturer')

class AsiaGlobalDriveAxleModel(models.Model):
	_name = 'asiaglobal.drive_axlemodel'

	name = fields.Char(required=True)
	manufacturer = fields.Many2one('asiaglobal.manufacturer')

class AsiaGlobalTransmissionModel(models.Model):
	_name = 'asiaglobal.transmission_model'

	name = fields.Char(required=True)
	manufacturer = fields.Many2one('asiaglobal.manufacturer')

class AsiaGlobalMastType(models.Model):
	_name = 'asiaglobal.mast_type'

	name = fields.Char(required=True)

class AsiaGlobalEquipmentProfile(models.Model):
	_name = 'asiaglobal.equipment_profile'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True, string='Equipment Profile')
	customer = fields.Many2one('res.partner', ondelete='cascade')

	manufacturer = fields.Many2one('asiaglobal.manufacturer')
	model = fields.Many2one('asiaglobal.manufacturer_model')
	serial_number = fields.Char()

	type = fields.Many2one('asiaglobal.equipment_type')
	capacity = fields.Char()
	date_in_service = fields.Date(default=fields.Datetime.now())

	engine_make = fields.Many2one('asiaglobal.manufacturer')
	engine_model = fields.Many2one('asiaglobal.engine_model')
	engine_serial_number = fields.Char()

	transmission_make = fields.Many2one('asiaglobal.manufacturer')
	transmission_model = fields.Many2one('asiaglobal.transmission_model')
	transmission_serial_number = fields.Char()

	drive_axle_manufacturer = fields.Many2one('asiaglobal.manufacturer')
	drive_axle_model = fields.Many2one('asiaglobal.drive_axlemodel')
	drive_axle_serial_number = fields.Char()

	traction_battery_capacity = fields.Char()
	traction_battery_serial_number = fields.Char()

	mast_type = fields.Many2one('asiaglobal.mast_type')
	mast_serial_number = fields.Char()
	forks = fields.Char()
	lift_height = fields.Char()
	gross_weight = fields.Char()