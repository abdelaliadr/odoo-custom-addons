from odoo import fields, models


class ServiceContract(models.Model):
    _name = "service.contract"
    _description = "Service Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    name = fields.Char(string="Reference", required=True, copy=False)
    active = fields.Boolean(string="Actif", default=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer",
        required=True, ondelete="cascade"
    )
    contract_type = fields.Selection([
        ("standard", "Standard"),
        ("premium", "Premium"),
        ("urgence", "24/7 Emergency"),
    ], string="Contract Type", default="standard", required=True)
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date")
    product_ids = fields.Many2many(
        "product.product",
        "service_contract_product_rel",
        "contract_id", "product_id",
        string="Covered Products"
    )
    intervention_ids = fields.One2many(
        "service.intervention", "contract_id",
        string="Interventions"
    )