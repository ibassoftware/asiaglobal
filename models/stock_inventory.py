from odoo import models, fields, api, _ 

class StockInventory(models.Model):
	_inherit = 'stock.inventory'

	@api.multi
	def inv_adj_account_entry_move(self):
		for move in self.move_ids:
			if not move.account_move_ids and move.value != 0:
				move.with_context(force_period_date=move.date)._account_entry_move()