# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AsiaGlobalManufacturer(models.Model):
	_name = 'asiaglobal.manufacturer'

	name = fields.Char(required=True)

class AsiaGlobalManufacturerModel(models.Model):
	_name = 'asiaglobal.manufacturer_model'

	name = fields.Char(required=True)
	manufacturer = fields.Many2one('asiaglobal.manufacturer')