from odoo import fields, models, api


class ServiceTechnician(models.Model):
    _name = "service.technician"
    _description = "Technician"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    user_id = fields.Many2one(
        "res.users", string="Linked User",
        help="Odoo user corresponding to this technician,"
             "useful for filtering 'My Interventions'."
    )
    team_id = fields.Many2one(
        "service.team", string="Team",
        ondelete="restrict"
    )
    phone = fields.Char(string="Phone")
    intervention_ids = fields.One2many(
        "service.intervention", "technician_id",
        string="Interventions"
    )
    intervention_count = fields.Integer(
        string="Number of Interventions",
        compute="_compute_intervention_count"
    )

    @api.depends("intervention_ids")
    def _compute_intervention_count(self):
        for tech in self:
            tech.intervention_count = len(tech.intervention_ids)