# -*- coding: utf-8 -*-
{
    'name': "Insight Project — Purchase Integration",
    'summary': "Vincula costos extra de escenarios a compras reales (purchase.order)",
    'version': '17.0.1.0.0',
    'category': 'Project',
    'author': "Cristian S. Rocha <csrocha@gmail.com>",
    'website': "https://github.com/csrocha/insight_project_purchase",
    'license': 'OPL-1',
    'depends': ['insight_project', 'purchase'],
    'data': [
        'views/insight_cost_budget_views.xml',
    ],
    'installable': True,
    'application': False,
}
