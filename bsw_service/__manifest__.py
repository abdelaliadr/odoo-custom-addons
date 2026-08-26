{
    "name": "Service & Interventions",
    "version": "19.0.1.0.0",
    "category": "Services",
    "summary": "Gestion des interventions techniques et du parc client",
    "author": "ATLAS SERVICES",
    "license": "LGPL-3",
    "depends": ["base", "mail", "product", "stock"],
    "data": [
        "security/ir_model.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/service_team_views.xml",
        "views/service_technician_views.xml",
        "views/service_equipment_views.xml",
        "views/service_contract_views.xml",
        "views/service_intervention_views.xml",
        "views/service_menus.xml",
        "report/service_intervention_report.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "application": True,
    "installable": True,
    "assets": {
    "web.assets_backend": [
        "bsw_service/static/src/scss/service_intervention.scss",
    ],
},
}