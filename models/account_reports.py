import calendar
import copy
import json
import io
import logging
import lxml.html

try:
	from odoo.tools.misc import xlsxwriter
except ImportError:
	# TODO saas-17: remove the try/except to directly import from misc
	import xlsxwriter

from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.tools import config
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


import logging
_logger = logging.getLogger(__name__)

class AccountReport(models.AbstractModel):
	_inherit = 'account.aged.receivable'

	def get_reports_buttons(self):
		return [{'name': _('Print Preview'), 'action': 'print_pdf'}, {'name': _('Export (XLSX)'), 'action': 'print_xlsx'}, {'name': _('Export (AR)'), 'action': 'print_xlsx_ar'}]

	def print_xlsx_ar(self, options):
		# _logger.info('SUNIKA')
		# context = self.env.context
		# _logger.info(context)
		# return {
		# 	'type' : 'ir.actions.act_url',
		# 	'url': '/web/export_xls/ar?filename=%s&company_id=%s&target_move=%s&sort_selection=%s&amount_currency=%s&date_from=%s&date_to=%s&journal_ids=%s'%(filename,company_id,target_move,sort_selection,amount_currency,date_from,date_to,journal_ids),
		# 	'target': 'self',
		# }
		return {
				'type': 'ir_actions_account_report_download',
				'data': {'model': self.env.context.get('model'),
						 'options': json.dumps(options),
						 'output_format': 'xlsx',
						 'financial_id': self.env.context.get('id'),
						 }
				}

	def get_xlsx(self, options, response):
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		sheet = workbook.add_worksheet(self.get_report_name()[:31])

		def_style = workbook.add_format({'font_name': 'Arial'})
		title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
		level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
		level_0_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'left': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
		level_0_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'right': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
		level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2})
		level_1_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'left': 2})
		level_1_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'right': 2})
		level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2})
		level_2_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2, 'left': 2})
		level_2_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2, 'right': 2})
		level_3_style = def_style
		level_3_style_left = workbook.add_format({'font_name': 'Arial', 'left': 2})
		level_3_style_right = workbook.add_format({'font_name': 'Arial', 'right': 2})
		domain_style = workbook.add_format({'font_name': 'Arial', 'italic': True})
		domain_style_left = workbook.add_format({'font_name': 'Arial', 'italic': True, 'left': 2})
		domain_style_right = workbook.add_format({'font_name': 'Arial', 'italic': True, 'right': 2})
		upper_line_style = workbook.add_format({'font_name': 'Arial', 'top': 2})

		sheet.set_column(0, 0, 15) #  Set the first column width to 15

		sheet.write(0, 0, '', title_style)

		y_offset = 4
		# if self.get_report_obj().get_name() == 'coa' and self.get_special_date_line_names():
		sheet.write(0, 0, 'ASIAGLOBAL TECHNOLOGIES, INC.', title_style)
		sheet.write(1, 0, 'AR AGING', title_style)
		sheet.write(2, 0, 'As of ', title_style)
		#     sheet.write(y_offset, 1, '', title_style)
		#     x = 2
		#     for column in self.with_context(is_xls=True).get_special_date_line_names():
		#         sheet.write(y_offset, x, column, title_style)
		#         sheet.write(y_offset, x+1, '', title_style)
		#         x += 2
		#     sheet.write(y_offset, x, '', title_style)
		#     y_offset += 1

		x = 0
		for column in self.get_columns_name(options):
			sheet.write(y_offset, x, column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' '), title_style)
			x += 1
		y_offset += 1
		ctx = self.set_context(options)
		ctx.update({'no_format':True, 'print_mode':True})
		lines = self.with_context(ctx).get_lines(options)

		if options.get('hierarchy'):
			lines = self.create_hierarchy(lines)

		if lines:
			max_width = max([len(l['columns']) for l in lines])

		for y in range(0, len(lines)):
			if lines[y].get('level') == 0:
				for x in range(0, len(lines[y]['columns']) + 1):
					sheet.write(y + y_offset, x, None, upper_line_style)
				y_offset += 1
				style_left = level_0_style_left
				style_right = level_0_style_right
				style = level_0_style
			elif lines[y].get('level') == 1:
				for x in range(0, len(lines[y]['columns']) + 1):
					sheet.write(y + y_offset, x, None, upper_line_style)
				y_offset += 1
				style_left = level_1_style_left
				style_right = level_1_style_right
				style = level_1_style
			elif lines[y].get('level') == 2:
				style_left = level_2_style_left
				style_right = level_2_style_right
				style = level_2_style
			elif lines[y].get('level') == 3:
				style_left = level_3_style_left
				style_right = level_3_style_right
				style = level_3_style
			# elif lines[y].get('type') != 'line':
			#     style_left = domain_style_left
			#     style_right = domain_style_right
			#     style = domain_style
			else:
				style = def_style
				style_left = def_style
				style_right = def_style
			sheet.write(y + y_offset, 0, lines[y]['name'], style_left)
			for x in range(1, max_width - len(lines[y]['columns']) + 1):
				sheet.write(y + y_offset, x, None, style)
			for x in range(1, len(lines[y]['columns']) + 1):
				# if isinstance(lines[y]['columns'][x - 1], tuple):
					# lines[y]['columns'][x - 1] = lines[y]['columns'][x - 1][0]
				if x < len(lines[y]['columns']):
					sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, lines[y]['columns'][x - 1].get('name', ''), style)
				else:
					sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, lines[y]['columns'][x - 1].get('name', ''), style_right)
			if 'total' in lines[y].get('class', '') or lines[y].get('level') == 0:
				for x in range(len(lines[0]['columns']) + 1):
					sheet.write(y + 1 + y_offset, x, None, upper_line_style)
				y_offset += 1
		if lines:
			for x in range(max_width + 1):
				sheet.write(len(lines) + y_offset, x, None, upper_line_style)

		workbook.close()
		output.seek(0)
		response.stream.write(output.read())
		output.close()