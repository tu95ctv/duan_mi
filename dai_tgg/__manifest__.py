# -*- coding: utf-8 -*-
{
    'name': "dai_tgg",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        NDT update 2510,04/06
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','base_import','hr','stock','downloadwizard'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ctr.xml',
        'views/cvi_form.xml',
        'views/cvi.xml',
        'views/tvcv.xml',
        'views/importthuvien.xml',
        'views/comment.xml',
        'views/config.xml',
#         'views/ghichucongviec.xml',
        'views/user.xml',
        'views/partner.xml',
        'views/download_cvi.xml',
        'views/file.xml',
        'views/to_trinh.xml',
        'views/department.xml',
        'views/download.xml',
                'views/tb.xml',

        'data/data.xml',
        'security/trucca_security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}