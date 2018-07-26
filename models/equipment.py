# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import *

import logging
_logger = logging.getLogger(__name__)

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
	customer = fields.Many2one('res.partner', ondelete='cascade', required=True)

	manufacturer = fields.Many2one('asiaglobal.manufacturer')
	model = fields.Many2one('asiaglobal.manufacturer_model')
	serial_number = fields.Char()

	date_in_service = fields.Date(required=True, default=fields.Datetime.now())
	type = fields.Many2one('asiaglobal.equipment_type')
	capacity = fields.Char()

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

	maintenance_frequency_count = fields.Integer()
	maintenance_frequency = fields.Selection([
		('day', 'Days'),
		('week', 'Weeks'),
		('month', 'Months'),
		('year', 'Years'),
	], default='day')
	next_maintenance_date = fields.Date(default=fields.Datetime.now())

	@api.model
	def create(self, vals):
		date_in_service = vals.get('date_in_service')
		count = vals.get('maintenance_frequency_count')
		frequency = vals.get('maintenance_frequency')
		if date_in_service and count and frequency:
			vals['next_maintenance_date'] = self.get_maintenance_date(date_in_service,count,frequency)

		result = super(AsiaGlobalEquipmentProfile, self).create(vals)
		return result

	@api.model
	def create_job(self):

		_logger.info('HOWDY')

		targetdate = datetime.today().strftime("%Y-%m-%d")
		for_maintenance = self.search([('next_maintenance_date','=',targetdate)],order='customer')

		_logger.info(targetdate)
		_logger.info(for_maintenance)
		if for_maintenance:
			# job_order = self.env['asiaglobal.job_order']

			for maintenance in for_maintenance:
				values = {
					'customer_id': maintenance.customer.id,
					'equipment_id': maintenance.id,
					'manufacturer': maintenance.manufacturer.id,
					'model': maintenance.model.id,
					'serial_number': maintenance.serial_number,
					'scheduled_date': maintenance.next_maintenance_date,
				}                
				job_order = self.env['asiaglobal.job_order'].create(values)

				if job_order:
					# UPDATE MAINTENANCE DATE
					new_maintenance_date = self.get_maintenance_date(targetdate, maintenance.maintenance_frequency_count, maintenance.maintenance_frequency)

					if new_maintenance_date:
						maintenance.write({'next_maintenance_date': new_maintenance_date})
		return

	def get_maintenance_date(self, date, count, frequency):
		new_maintenance_date = False

		if frequency == 'day':
			days = count
			new_maintenance_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=days)).strftime("%Y-%m-%d")

		if frequency == 'week':
			days = count * 7
			new_maintenance_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=days)).strftime("%Y-%m-%d")

		if frequency == 'month':
			months = count
			new_maintenance_date = (datetime.strptime(date, '%Y-%m-%d') + relativedelta(months=months)).strftime("%Y-%m-%d")

		if frequency == 'year':
			years = count
			new_maintenance_date = (datetime.strptime(date, '%Y-%m-%d') + relativedelta(years=years)).strftime("%Y-%m-%d")

		return new_maintenance_date