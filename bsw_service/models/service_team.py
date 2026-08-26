from odoo import fields, models


class ServiceTeam(models.Model):
    _name = "service.team"
    _description = "Équipe technique"
    _order = "name"

    name = fields.Char(string="Nom de l'équipe", required=True)
    active = fields.Boolean(string="Actif", default=True)
    member_ids = fields.One2many(
        "service.technician", "team_id",
        string="Technicians"
    )

    member_count = fields.Integer(
        string="Nombre de technicians",
        compute="_compute_member_count"
    )

    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)