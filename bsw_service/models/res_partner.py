from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    service_intervention_count = fields.Integer(
        string="Nombre d'interventions",
        compute="_compute_service_intervention_count"
    )
    service_level = fields.Selection([
    ("standard", "Standard"),
    ("premium", "Premium"),
    ("vip", "VIP"),], string="Niveau de service", default="standard")

    def _compute_service_intervention_count(self):
        for partner in self:
            partner.service_intervention_count = self.env["service.intervention"].search_count(
                [("partner_id", "=", partner.id)]
            )

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