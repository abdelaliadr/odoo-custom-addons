from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    service_intervention_ids = fields.One2many(
        "service.intervention", "invoice_id",
        string="Linked Interventions"
    )