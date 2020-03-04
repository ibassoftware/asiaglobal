from odoo import models, fields, api
import logging
import re
from odoo.exceptions import UserError, AccessError, ValidationError


class AGTCRMTeam(models.Model):

	_inherit = 'crm.team'

	minimum_gross_margin = fields.Float(
		string='(Indent) Minimum GM without CEO Approval',
		default = 0
	)

	maximum_gross_value = fields.Float(
		string='(Indent) Maximum Gross Value without CEO Approval',
		default = 0
	)

	minimum_gross_margin_forward = fields.Float(
		string='(Forward) Minimum GM without CEO Approval',
		default = 0
	)

	maximum_gross_value_forward = fields.Float(
		string='(Forward) Maximum Gross Value without CEO Approval',
		default = 0
	)

	minimum_gross_margin_part = fields.Float(
		string='(Part Sales) Minimum GM without CEO Approval',
		default = 0
	)

	maximum_gross_value_part = fields.Float(
		string='(Part Sales) Maximum Gross Value without CEO Approval',
		default = 0
	)

	minimum_gross_margin_service = fields.Float(
		string='(Service) Minimum GM without CEO Approval',
		default = 0
	)

	maximum_gross_value_service = fields.Float(
		string='(Service) Maximum Gross Value without CEO Approval',
		default = 0
	)