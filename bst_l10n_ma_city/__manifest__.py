{
    'name': 'Maroc - Référentiel des villes',
    'version': '19.0.1.0.0',
    'category': 'Localization',
    'summary': "Référentiel des villes et codes postaux du Maroc",
    'description': """
Charge le référentiel des villes du Maroc (res.city) avec code postal
et région, et active la sélection de ville par liste déroulante sur
les contacts marocains.
    """,
    'author': 'Blackswan Technology',
    'depends': ['base_address_extended'],
    'data': [
       'data/res_country_data.xml',
       'data/res.country.state.csv',
       'data/res.city.csv',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}