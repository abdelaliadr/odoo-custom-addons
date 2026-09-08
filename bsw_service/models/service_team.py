from odoo import fields, models, api


class ServiceTeam(models.Model):
    _name = "service.team"
    _description = "Technical Team"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Team Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    member_ids = fields.One2many(
        "service.technician", "team_id",
        string="Technicians"
    )

    member_count = fields.Integer(
        string="Number of Technicians",
        compute="_compute_member_count"
    )

    manager_id = fields.Many2one(
    "service.technician", string="Manager",
    help="Technician responsible for this team,"
         "who can see all interventions assigned to its members.")
    
    @api.depends("member_ids")
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)