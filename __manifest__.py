# -*- coding: utf-8 -*-
{
    'name': "asiaglobal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale_management', 'purchase','hr', 'helpdesk', 'sales_team', 'r2d2',
    'sale','sale_crm', 'mail', 'sale_subscription', 'product'],

    # always loaded
    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/report_paperformat_data.xml',
        'data/subscription_template.xml',
        'views/ir_cron.xml',
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
        'views/job_order_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/service_report_views.xml',
        'views/service_menu.xml',
        'report/report_quotation_service.xml',
        'report/service_report.xml',
        'report/report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}