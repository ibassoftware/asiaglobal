from odoo import models, fields, api, _ 

# from collections import defaultdict

class StockMove(models.Model):
	_inherit = 'stock.move'

	product_id_code = fields.Char(string='Item Code', compute='_get_product_details')
	product_id_partno =  fields.Char(string='Part Number', compute='_get_product_details')
	product_id_description = fields.Char(string='Description', compute='_get_product_details')
	location = fields.Char()

	@api.multi
	@api.depends('product_id')
	def _get_product_details(self):
		for record in self:
			record.product_id_code = record.product_id.default_code
			record.product_id_partno = record.product_id.name
			record.product_id_description = record.product_id.description_sale

	# @api.multi
	# def _inv_adj_account_entry_move(self):
	# 	for move in self:
	# 		""" Accounting Valuation Entries - BEGINNING - INV ADJ """
	# 		location_from = move.location_id
	# 		location_to = move.location_dest_id  # TDE FIXME: as the accounting is based on this value, should probably check all location_to to be the same
	# 		company_from = location_from.usage == 'internal' and location_from.company_id or False
	# 		company_to = location_to and (location_to.usage == 'internal') and location_to.company_id or False

	# 		# Create Journal Entry for products arriving in the company; in case of routes making the link between several
	# 		# warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
	# 		if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
	# 			journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
	# 			move.with_context(force_company=company_to.id)._create_account_move_line(acc_src, acc_valuation, journal_id)

	# def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
	# 	# group quants by cost
	# 	move_cost_qty = defaultdict(lambda: 0.0)
	# 	for move in self:
	# 		move_cost_qty[move.price_unit] += move.product_uom_qty

	# 	AccountMove = self.env['account.move']
	# 	for cost, qty in move_cost_qty.iteritems():
	# 		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
	# 		if move_lines:
	# 			date = self.date
	# 			new_account_move = AccountMove.create({
	# 				'journal_id': journal_id,
	# 				'line_ids': move_lines,
	# 				'date': date,
	# 				'ref': self.reference})
	# 			new_account_move.post()

class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	value = fields.Float(related="move_id.value", copy=False)
	remaining_qty = fields.Float(related="move_id.remaining_qty", copy=False)
	remaining_value = fields.Float(related="move_id.remaining_value", copy=False)
	price_unit = fields.Float(related="move_id.price_unit", string='Unit Price', copy=False)