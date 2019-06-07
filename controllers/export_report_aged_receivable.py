# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import deque
import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.misc import xlwt

from datetime import datetime
from datetime import date

import logging
_logger = logging.getLogger(__name__)

class ExportReportAR(http.Controller):

	@http.route('/web/export_xls/ar', type='http', auth="user")
	def export_xls(self, filename, company_id, target_move, sort_selection, amount_currency, date_from, date_to, journal_ids, **kw):
		company_id = request.env.user.company_id
		amount_currency = bool(amount_currency)

		# TARGET MOVE
		if target_move == 'posted':
			target_move = 'All Posted Entries'
		else:
			target_move = 'All Entries'
		
		# SORT SELECTION
		if sort_selection == 'move_name':
			sort_selection = 'Journal Entry Number'
		else:
			sort_selection = 'Date'
		
		user_id = request.env.user.name

		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Sales/Purchase Journal')
		# STYLES
		style_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: wrap no")
		style_header_right = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no")
		style_header_left = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no")
		style_table_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz centre, vert centre, wrap on;borders: bottom medium;")
		style_table_row = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: bottom thin;")
		style_table_row_date = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: bottom thin;", num_format_str = 'yyyy-mm-dd')
		style_table_row_amount = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: bottom thin;", num_format_str="#,##0.00")
		style_table_row_amount_currency = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: bottom thin;")

		style_table_total = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz left, wrap no;")
		style_table_total_value = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz right, wrap no;", num_format_str="#,##0.00")
		style_end_report = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz left, wrap no;")
		
		worksheet.col(0).width = 450*12
		worksheet.col(1).width = 250*12
		worksheet.col(2).width = 250*12
		worksheet.col(3).width = 350*12
		worksheet.col(4).width = 650*12
		worksheet.col(5).width = 650*12
		worksheet.col(6).width = 350*12
		worksheet.col(7).width = 250*12
		worksheet.col(8).width = 350*12
		worksheet.col(9).width = 750*12
		worksheet.col(10).width = 250*12
		worksheet.col(11).width = 250*12
		worksheet.col(12).width = 250*12
		worksheet.col(13).width = 350*12
		worksheet.col(14).width = 350*12
		worksheet.col(15).width = 350*12
		worksheet.col(16).width = 350*12
		worksheet.col(17).width = 750*12
		worksheet.col(18).width = 350*12
		worksheet.col(19).width = 350*12
		worksheet.col(20).width = 350*12
		worksheet.col(21).width = 150*12

		# # HEADERS
		worksheet.write(2, 0, 'COMPANY NAME: ', style_header_bold)
		worksheet.write(2, 1, company_id.name, style_header_left)

		worksheet.write(3, 0, 'COMPANY TIN: ', style_header_bold)
		worksheet.write(3, 1, company_id.vat, style_header_left)

		worksheet.write(4, 0, 'PERIOD COVERED: ', style_header_bold)
		worksheet.write(4, 1, str(date_from) + " to " + str(date_to), style_header_left)

		# TABLE HEADER
		worksheet.write(6, 0, 'JOURNAL', style_table_header_bold) # HEADER
		worksheet.write(6, 1, 'DATE', style_table_header_bold) # HEADER
		worksheet.write(6, 2, 'COUNTRY', style_table_header_bold) # HEADER
		worksheet.write(6, 3, 'TIN', style_table_header_bold) # HEADER
		worksheet.write(6, 4, 'PARTNER', style_table_header_bold) # HEADER
		worksheet.write(6, 5, 'DELIVERED TO', style_table_header_bold) # HEADER
		worksheet.write(6, 6, 'PRODUCT TYPE', style_table_header_bold) # HEADER
		worksheet.write(6, 7, 'HS CODE', style_table_header_bold) # HEADER
		worksheet.write(6, 8, 'PRODUCT CODE', style_table_header_bold) # HEADER
		worksheet.write(6, 9, 'PRODUCT NAME', style_table_header_bold) # HEADER
		worksheet.write(6, 10, 'UOM', style_table_header_bold) # HEADER
		worksheet.write(6, 11, 'WEIGHT', style_table_header_bold) # HEADER
		worksheet.write(6, 12, 'QTY', style_table_header_bold) # HEADER
		worksheet.write(6, 13, 'UNIT COST', style_table_header_bold) # HEADER
		worksheet.write(6, 14, 'REFERENCE', style_table_header_bold) # HEADER
		worksheet.write(6, 15, 'JOURNAL ENTRY', style_table_header_bold) # HEADER
		worksheet.write(6, 16, 'ACCOUNT CODE', style_table_header_bold) # HEADER
		worksheet.write(6, 17, 'ACCOUNT TITLE', style_table_header_bold) # HEADER
		worksheet.write(6, 18, 'DEBIT', style_table_header_bold) # HEADER
		worksheet.write(6, 19, 'CREDIT', style_table_header_bold) # HEADER

		if amount_currency == True:
			worksheet.write(6, 20, 'CURRENCY', style_table_header_bold) # HEADER
			worksheet.write(6, 21, 'CURRENCY SYMBOL', style_table_header_bold) # HEADER

		row_count = 7
		total_qty = 0
		total_debit = 0
		total_credit = 0
		journal_ids = eval('[' + journal_ids + ']')

		for journal in journal_ids:
			# journal_data = request.env['account.journal'].search([('id', '=', journal)])
			move_lines = request.env['account.move.line'].search([('journal_id.id', '=', journal),('date','>=',date_from),('date','<=',date_to)],order="date asc")
			for move in move_lines:
				product_type = ''
				if move.product_id.type == 'product':
					product_type = 'Stockable Product'
				elif move.product_id.type == 'consu':
					product_type = 'Consumable'
				else:
					product_type = 'Service'

				# DATE
				move_line_date = datetime.strptime(move.date, "%Y-%m-%d")
				# _logger.info(move_line_date)
				 
				worksheet.write(row_count, 0, move.journal_id.name, style_table_row)
				worksheet.write(row_count, 1, move_line_date, style_table_row_date)
				worksheet.write(row_count, 2, move.partner_id.country_id.name or '', style_table_row)
				worksheet.write(row_count, 3, move.partner_id.vat or '', style_table_row)
				worksheet.write(row_count, 4, move.partner_id.name or '', style_table_row)
				worksheet.write(row_count, 5, move.partner_id.name or '', style_table_row)
				worksheet.write(row_count, 6, product_type, style_table_row)
				worksheet.write(row_count, 7, move.product_id.hs_code or move.product_id.tariff_code or '', style_table_row)
				worksheet.write(row_count, 8, move.product_id.code or '', style_table_row)
				worksheet.write(row_count, 9, move.product_id.name or '', style_table_row)
				worksheet.write(row_count, 10, move.product_uom_id.name or '', style_table_row)
				worksheet.write(row_count, 11, move.product_id.weight or '', style_table_row_amount)
				worksheet.write(row_count, 12, move.quantity, style_table_row_amount)
				worksheet.write(row_count, 13, move.product_id.lst_price, style_table_row_amount)
				worksheet.write(row_count, 14, move.ref or '', style_table_row)
				worksheet.write(row_count, 15, move.move_id.name, style_table_row)
				worksheet.write(row_count, 16, move.account_id.code or '', style_table_row)
				worksheet.write(row_count, 17, move.account_id.name or '', style_table_row)
				worksheet.write(row_count, 18, move.debit, style_table_row_amount)
				worksheet.write(row_count, 19, move.credit, style_table_row_amount)
				if amount_currency == True:
					worksheet.write(row_count, 20, move.amount_currency, style_table_row_amount)
					worksheet.write(row_count, 21, move.currency_id.symbol or '', style_table_row)
				total_qty +=  move.quantity
				total_debit += move.debit
				total_credit += move.credit
				row_count += 1

		table_total_start = row_count

		# TABLE TOTALS
		worksheet.write(table_total_start, 0,  'Total', style_table_total)
		worksheet.write(table_total_start, 12,  total_qty, style_table_total_value)
		worksheet.write(table_total_start, 18,  total_debit, style_table_total_value)
		worksheet.write(table_total_start, 19,  total_credit, style_table_total_value)

		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', 'attachment; filename=%s;'%(filename)
					)])

		workbook.save(response.stream)

		return response
