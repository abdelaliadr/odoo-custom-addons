from odoo import fields, models


class ServiceTechnician(models.Model):
    _name = "service.technician"
    _description = "Technicien"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(string="Actif", default=True)
    user_id = fields.Many2one(
        "res.users", string="Utilisateur lié",
        help="Utilisateur Odoo correspondant à ce technicien, "
             "utile pour filtrer 'mes interventions'."
    )
    team_id = fields.Many2one(
        "service.team", string="Équipe",
        ondelete="restrict"
    )
    phone = fields.Char(string="Téléphone")
    intervention_ids = fields.One2many(
        "service.intervention", "technician_id",
        string="Interventions"
    )
    intervention_count = fields.Integer(
        string="Nombre d'interventions",
        compute="_compute_intervention_count"
    )

    def _compute_intervention_count(self):
        for tech in self:
            tech.intervention_count = len(tech.intervention_ids)