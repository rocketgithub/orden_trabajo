# -*- coding: utf-8 -*-
{
    'name': "Ordenes de Trabajo",

    'summary': """ Módulo de ordenes de trabajo """,

    'description': """
         Módulo para ordenes de trabajo
    """,

    'author': "Rodolfo Borstcheff",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'sale'],

    'data': [
        'views/orden_trabajo_views.xml',
        'security/ir.model.access.csv',
    ],
}
