from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from werkzeug import url_encode


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = 'hr.expense.sheet.register.payment.wizard'

    def _get_payment_value(self):
        """ Hook for extension """
        return {
            'payment_date': self.payment_date,
            'memo': self.communication
        }

    @api.multi
    def expense_post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)

        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.post()

        # expense update
        expense_sheet.update(self._get_payment_value())

        # Log the payment in the chatter
        body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") %
                (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)

        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable' and not line.reconciled:
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()

        return {'type': 'ir.actions.act_window_close'}


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    expense_line_ids = fields.One2many(
        states={'done': [('readonly', True)], 'post': [('readonly', True)]})

    payment_date = fields.Date(string='Payment Date')
    memo = fields.Char(string='Memo')


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    unit_amount = fields.Float(digits=dp.get_precision('Sale Product Price'))
