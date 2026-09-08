from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    intervention_ids = fields.One2many(
        "service.intervention",
        "partner_id",
        string="Interventions",
    )

    service_intervention_count = fields.Integer(
        string="Number of Interventions",
        compute="_compute_service_intervention_count"
    )
    service_level = fields.Selection([
    ("standard", "Standard"),
    ("premium", "Premium"),
    ("vip", "VIP"),], string="Service Level", default="standard")

    @api.depends("intervention_ids")
    def _compute_service_intervention_count(self):
        for partner in self:
            partner.service_intervention_count = len(partner.intervention_ids)
            

    def action_view_service_interventions(self):
        self.ensure_one()
        return {
            "name": "Interventions",
            "type": "ir.actions.act_window",
            "res_model": "service.intervention",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }