# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import re
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)


class AGTRentals(models.Model):

	_inherit = 'sale.subscription'

	state = fields.Selection([('draft', 'For Approval'), ('approved', 'Approved'), ('open', 'In Progress'), ('pending', 'To Renew'),
		('close', 'Closed'), ('cancel', 'Cancelled')],
		string='Status', required=True, track_visibility='onchange', copy=False, default='draft')

	principal_id = fields.Many2one(
		'res.partner',
		string='Principal',
		domain=[('is_principal','=',True), ]
	)

	project_stage_id = fields.Many2one(
		'asiaglobal.stages',
		string='Project Stage',
		track_visibility='onchange',
	)

	project_probability = fields.Float(
		string='Probability %',
		compute= '_compute_probability',
		store=True,
	)

	@api.depends('project_stage_id')
	@api.one
	def _compute_probability(self):
		if (self.project_stage_id):
			self.project_probability = self.project_stage_id.probability

	def admin_approval(self):
		self.state = "approved"	

	project_description = fields.Char(
		string='Project Description',
		required=True,
	)

	team_id = fields.Many2one(
	    'crm.team',
	    string='Sales Channel',
	)

