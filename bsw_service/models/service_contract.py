from odoo import fields, models


class ServiceContract(models.Model):
    _name = "service.contract"
    _description = "Contrat de service"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    name = fields.Char(string="Référence", required=True, copy=False)
    active = fields.Boolean(string="Actif", default=True)
    partner_id = fields.Many2one(
        "res.partner", string="Client",
        required=True, ondelete="cascade"
    )
    contract_type = fields.Selection([
        ("standard", "Standard"),
        ("premium", "Premium"),
        ("urgence", "Urgence 24/7"),
    ], string="Type de contrat", default="standard", required=True)
    date_start = fields.Date(string="Date de début", required=True)
    date_end = fields.Date(string="Date de fin")
    product_ids = fields.Many2many(
        "product.product",
        "service_contract_product_rel",
        "contract_id", "product_id",
        string="Produits couverts"
    )
    intervention_ids = fields.One2many(
        "service.intervention", "contract_id",
        string="Interventions"
    )