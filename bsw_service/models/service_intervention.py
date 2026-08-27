from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ServiceIntervention(models.Model):
    _name = "service.intervention"
    _description = "Intervention technique"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_planned desc, id desc"
    _name_unique = models.Constraint(
        "unique(name)",
        "La référence d'une intervention doit être unique !",
    )

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
    date_start = fields.Datetime(string="Date Début")
    date_end = fields.Datetime(string="Date Fin")
    duration = fields.Float(
    string="Durée de l'intervention (heures)", compute="_compute_duration",
    store=True, digits=(6, 2))
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
    amount_parts = fields.Monetary(string="Coût des pièces", currency_field="currency_id", compute="_compute_amount_parts", store=True)
    currency_id = fields.Many2one(
    "res.currency", string="Devise",
    related="company_id.currency_id", store=True, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "service.intervention") or "Nouveau"
        return super().create(vals_list)

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for intervention in self:
            if intervention.date_start and intervention.date_end:
                duration_count = intervention.date_end - intervention.date_start
                intervention.duration = duration_count.total_seconds() / 3600.0
            else:
                intervention.duration = 0.0

    @api.depends("line_ids.quantity", "line_ids.price_unit")
    def _compute_amount_parts(self):
        for intervention in self:
            intervention.amount_parts = sum(
            line.quantity * line.price_unit
            for line in intervention.line_ids)

    def action_plan(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Seule une intervention en brouillon peut être planifiée."))
        if not self.technician_id:
            raise UserError(_("Un technicien est obligatoire pour planifier."))
        self.state = "planned"

    def action_start(self):
        self.ensure_one()
        if self.state != "planned":
            raise UserError(_("Seule une intervention planifiée peut être démarrée."))
        self.date_start = fields.Datetime.now()
        self.state = "in_progress"

    def action_done(self):
        self.ensure_one()
        if self.state != "in_progress":
            raise UserError(_("Seule une intervention en cours peut être terminée."))
        self.date_end = fields.Datetime.now()
        self.state = "done"

    def action_invoice(self):
        self.ensure_one()
        if self.state != "done":
            raise UserError(_("Seule une intervention terminée peut être facturée."))
        self.state = "invoiced"

    def action_reset_draft(self):
        self.ensure_one()
        if self.state == "invoiced":
            raise UserError(_("Une intervention facturée ne peut pas repasser en brouillon."))
        self.state = "draft"

    @api.constrains("state", "technician_id")
    def _check_technician_exists(self):
        for intervention in self:
            if intervention.state != "draft" and not intervention.technician_id:
                raise UserError(_("Une intervention nécessite un technicien dès qu'elle n'est plus en brouillon."))

    @api.constrains("date_start","date_end")
    def _check_dates(self):
        for intervention in self:
            if intervention.date_start and intervention.date_end and intervention.date_start > intervention.date_end:
                raise UserError("La date de fin ne peut pas préceder la date de début")

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.equipment_id = False
        if self.partner_id:
            equipment = self.env["service.equipment"].search([("partner_id", "=", self.partner_id.id)], limit=1)
            if equipment:
                self.equipment_id = equipment
                return {"domain": {"equipment_id": [("partner_id", "=", self.partner_id.id)]}}

    @api.ondelete(at_uninstall=False)
    def unlink_except_invoiced(self):
        for intervention in self:
            if intervention.state == "invoiced":
                raise UserError("Une intervention facturée ne peut pas être supprimée")               