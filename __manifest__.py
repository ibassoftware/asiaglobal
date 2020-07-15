# -*- coding: utf-8 -*-
{
    'name': "asiaglobal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm', 'sale_management', 'purchase','hr', 'hr_expense', 'helpdesk', 'sales_team', 'account_reports',
    'sale','sale_crm', 'mail', 'sale_subscription', 'product', 'stock', 'stock_account', 'account', 'account_budget', 'calendar', 'stock_analytic', 'ibas_agt', 
    'account_check_printing', 'l10n_us_check_printing'],

    # always loaded
    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/report_paperformat_data.xml',
        'data/report_data.xml',
        'data/subscription_template.xml',
        'data/timesheet_data.xml',
        'data/job_order_data.xml',
        'data/decimal_accuracy_data.xml',
        'views/assets.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/data.xml',
        'views/crm.xml',
        'views/crmsalesteamdata.xml',
        'views/rentals.xml',
        'views/productcategories.xml',
        'views/layout_templates.xml',
        'views/manufacturer_views.xml',
        'views/equipment_views.xml',
        'views/res_partner_views.xml',
        'views/hr_employee_views.xml',
        'views/job_order_timesheet_views.xml',
        'views/job_order_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/service_report_views.xml',
        'views/job_material_request_form_view.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_account_views.xml',
        'views/stock_move_update.xml',
        'views/account_invoice_view.xml',
        'views/calendar_views.xml',
        'views/hr_expense_views.xml',
        'views/stock_inventory_views.xml',
        'views/account_payment_view.xml',
        'report/report_quotation_service.xml',
        'report/service_report.xml',
        'report/report_job_order.xml',
        'report/report_job_material_request_form.xml',
        'report/report_invoice.xml',
        'report/report_job_order_stp.xml',
        'report/report_purchasequotation.xml',
        'report/report_purchaseorder.xml',
        'report/report_stock_item_receipt.xml',
        'report/report_payment_receipt.xml',
        'report/report_deliveryslip.xml',
        'report/report_account_payable_voucher.xml',
        'report/report_budget_view.xml',
        'report/report_print_check_views.xml',
        'report/report.xml',
        'views/service_menu.xml',
        'wizard/maintenance_jo_views.xml',
    ],

    'qweb': [
        'static/src/xml/web_calendar.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

# # -*- RCS -*-
