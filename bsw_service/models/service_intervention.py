from odoo import api, fields, models


class ServiceIntervention(models.Model):
    _name = "service.intervention"
    _description = "Intervention technique"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_planned desc, id desc"

    name = fields.Char(
        string="Référence", required=True, copy=False,
        readonly=True, default=lambda self: "Nouveau")
    partner_id = fields.Many2one(
        "res.partner", string="Client", required=True,
        ondelete="restrict", tracking=True)
    equipment_id = fields.Many2one(
        "service.equipment", string="Équipement",
        domain="[('partner_id', '=', partner_id)]")
    technician_id = fields.Many2one(
        "service.technician", string="Technicien", tracking=True)
    contract_id = fields.Many2one(
        "service.contract", string="Contrat",
        domain="[('partner_id', '=', partner_id)]")
    company_id = fields.Many2one(
    "res.company", string="Société",
    default=lambda self: self.env.company, required=True
)
    active = fields.Boolean(string="Actif", default=True)
    date_planned = fields.Datetime(string="Date planifiée")
    line_ids = fields.One2many(
        "service.intervention.line", "intervention_id",
        string="Pièces consommées")
    state = fields.Selection([
        ("draft", "Brouillon"),
        ("planned", "Planifiée"),
        ("in_progress", "En cours"),
        ("done", "Terminée"),
        ("invoiced", "Facturée"),
    ], string="Statut", default="draft", required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "service.intervention") or "Nouveau"
        return super().create(vals_list)