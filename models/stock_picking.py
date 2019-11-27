from odoo import models, fields, api, _ 

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	location = fields.Char()
	remarks = fields.Text()
	validated_by = fields.Many2one('res.users')

	@api.multi
	def button_validate(self):
		result = super(StockPicking, self).button_validate()
		for pick in self:
			pick.validated_by = self.env.user
		return result