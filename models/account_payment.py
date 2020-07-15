from odoo import models, fields, api, _
from num2words import num2words

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
	_inherit = 'account.payment'

	amount_in_words = fields.Char(string='Amount In words', compute='_onchange_amount', store=True)

	@api.depends('amount')
	@api.multi
	def _onchange_amount(self):
		for rec in self:
			whole = num2words(int(rec.amount)) + ' Pesos '
			whole = whole.replace(' and ',' ')
			if "." in str(rec.amount): # quick check if it is decimal
				decimal_no = str(rec.amount).split(".")[1]
				if len(decimal_no) == 1:
					decimal_no = decimal_no + "0"
			if decimal_no:
					whole = whole + "and " + decimal_no + '/100'
			whole = whole.replace(',','')
			rec.amount_in_words = whole.upper() + " ONLY"
			rec.check_amount_in_words = whole.upper() + " ONLY"

	# @api.model
	# def compute_check_amount_in_words(self):
	# 	for record in self.search([]):
	# 		if not record.check_amount_in_words:
	# 			check_amount_in_words = record.currency_id.amount_to_text(record.amount)
	# 			record.check_amount_in_words = check_amount_in_words

