from odoo import models, fields, api, _ 

class ProductProduct(models.Model):
	_inherit = 'product.product'

	default_code = fields.Char(string='Item Code')

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	default_code = fields.Char(string='Item Code')