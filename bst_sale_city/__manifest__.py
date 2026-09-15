{
    'name': 'Ville sur le devis et le bon de commande',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': "Ajoute la ville du client sur le devis, avec recherche, filtre et impression",
    'depends': ['sale', 'bst_l10n_ma_city'],
    'data': [
        'views/sale_order_views.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}