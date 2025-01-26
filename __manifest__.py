# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo 16 kMyMoney',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',
    'description': """
InfoSaône - Module Odoo 16 Module Odoo kMyMoney
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/is_kmymoney_view.xml',
        'views/is_kmymoney_report_view.xml',
        'views/is_suivi_sante_view.xml',
        'report/solde_par_mois_report.xml',
        'report/solde_par_an_report.xml',
        'report/solde_par_operation_report.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
