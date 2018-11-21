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
	_description = 'Equipment Profile'
	_inherit = ['mail.thread','mail.activity.mixin']

	@api.depends('job_expense_ids.amount_total')
	def _amount_all(self):
		"""
		Compute the total amounts of the Expense.
		"""
		for equipment in self:
			amount_expense_total = 0.0
			for expense in equipment.job_expense_ids:
				amount_expense_total += expense.amount_total
			equipment.update({
				'amount_expense_total':amount_expense_total,
			})

	@api.one
	def _compute_parts_fitted(self):
		parts_fitted = []
		for job in self.jo_ids:
			for report in job.service_report_ids:
				if report.is_parts_fitted == True and report.parts_fitted:
					for parts in report.parts_fitted:
						parts_fitted.append(parts.id)
		self.parts_fitted = parts_fitted

	@api.one
	def _compute_job_material_request(self):
		job_material_request = []
		for job in self.jo_ids:
			for request in job.job_material_request_ids:
				job_material_request.append(request.id)
		self.job_material_request_ids = job_material_request

	name = fields.Char(string='Equipment Profile', store=True, compute="_compute_name")
	customer = fields.Many2one('res.partner', ondelete='cascade', required=True, track_visibility='onchange')
	ship_to = fields.Many2one('res.partner', string='Ship To / Site Address')
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

	battery_1 = fields.Char()
	battery_1_type = fields.Char(string='Type')
	battery_1_serial = fields.Char(string='Serial Number')

	battery_2 = fields.Char()
	battery_2_type = fields.Char(string='Type')
	battery_2_serial = fields.Char(string='Serial Number')

	battery_3 = fields.Char()
	battery_3_type = fields.Char(string='Type')
	battery_3_serial = fields.Char(string='Serial Number')

	mast_type = fields.Many2one('asiaglobal.mast_type')
	mast_serial_number = fields.Char()
	forks = fields.Char()
	lift_height = fields.Char()
	gross_weight = fields.Char()

	maintenance_contract = fields.Boolean()
	maintenance_start_date = fields.Date(default=fields.Datetime.now())
	maintenance_end_date = fields.Date(default=fields.Datetime.now())
	maintenance_frequency_count = fields.Integer()
	maintenance_frequency = fields.Selection([
		('day', 'Days'),
		('week', 'Weeks'),
		('month', 'Months'),
		('year', 'Years'),
	], default='day')
	next_maintenance_date = fields.Date(default=fields.Datetime.now())

	hour_meter = fields.Float(compute="_compute_hour_meter")

	# WARRANTY
	warranty_date_acceptance = fields.Date(string='Date of Acceptance', default=fields.Datetime.now())
	warranty_year = fields.Float()
	warranty_hours = fields.Float()

	jo_ids = fields.One2many('asiaglobal.job_order', 'equipment_id', string='Job Orders', readonly=True)

	# RENTAL
	rental_date_start = fields.Date(string='Start of Rental Period')
	rental_date_end = fields.Date(string='End of Rental Period')

	equipment_owner_id = fields.Many2one('res.partner', string='Equipment Owner', track_visibility='onchange')
	
	operational = fields.Boolean(default=True)
	operational_message = fields.Char(string='Equipment Status', track_visibility='onchange')

	parts_fitted = fields.Many2many('asiaglobal.service_report_parts', string='Parts Fitted', compute='_compute_parts_fitted')

	job_expense_ids = fields.One2many('asiaglobal.job_expense', 'equipment_id', string='Job Expense')
	amount_expense_total = fields.Float(string='Total Other Repair Costs', store=True, readonly=True, compute='_amount_all', track_visibility='always')

	job_material_request_ids = fields.Many2many('asiaglobal.job_material_request_form', string='Job Material Request Form', compute='_compute_job_material_request')

	@api.multi
	@api.onchange('customer')
	def onchange_customer(self):
		if not self.customer:
			self.update({
				'ship_to': False,
			})
			return

		addr = self.customer.address_get(['delivery'])
		values = {
			'ship_to': addr['delivery'],
		}

		self.update(values)

	@api.onchange('operational')
	def set_operational_message(self):
		if self.operational == True:
			self.operational_message = "OPERATIONAL"
		else:
			self.operational_message = "NOT OPERATIONAL"

	@api.one
	@api.depends('customer','manufacturer','model','serial_number')
	def _compute_name(self):
		name = ''
		if self.customer:
			name += self.customer.name

		if self.manufacturer:
			name += ' - ' + self.manufacturer.name

		if self.model:
			name += ' - ' + self.model.name

		if self.serial_number:
			name += ' - ' + self.serial_number

		self.name = name

	@api.multi
	def _compute_hour_meter(self):
		for record in self:
			latest_service_report_hour_meter = 0
			latest_service_report_visit_date = False
			for job in record.jo_ids:
				for report in job.service_report_ids:
					if not latest_service_report_visit_date:
						latest_service_report_visit_date = report.visit_date
						latest_service_report_hour_meter = report.hour_meter
					if latest_service_report_visit_date < report.visit_date:
						latest_service_report_visit_date = report.visit_date
						latest_service_report_hour_meter = report.hour_meter

					_logger.info('BULRAEK')
					_logger.info(report.visit_date)
					_logger.info(latest_service_report_visit_date)
					_logger.info(latest_service_report_hour_meter)

			record.hour_meter = latest_service_report_hour_meter

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
	def create_maintenance_jo(self, equipment_id, date):
		values = {
			'customer_id': equipment_id.customer.id,
			'ship_to': equipment_id.ship_to.id,
			'equipment_id': equipment_id.id,
			'manufacturer': equipment_id.manufacturer.id,
			'model': equipment_id.model.id,
			'serial_number': equipment_id.serial_number,
			'scheduled_date': date,
			'actual_repair_date': date,
		}                
		job_order = self.env['asiaglobal.job_order'].create(values)
		return job_order