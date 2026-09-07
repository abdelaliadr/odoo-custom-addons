from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ServiceIntervention(models.Model):
    _name = "service.intervention"
    _description = "Technical Intervention"
    _order = "date_planned desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name_unique = models.Constraint(
        "unique(name)",
        "The intervention reference must be unique!",
    )

    name = fields.Char(
        string="Reference", required=True, copy=False,
        readonly=True, default=lambda self: "New")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True,
        ondelete="restrict", tracking=True)
    equipment_id = fields.Many2one(
        "service.equipment", string="Equipement",
        domain="[('partner_id', '=', partner_id)]")
    technician_id = fields.Many2one(
        "service.technician", string="Technician", tracking=True)
    contract_id = fields.Many2one(
        "service.contract", string="Contract",
        domain="[('partner_id', '=', partner_id)]")
    company_id = fields.Many2one(
    "res.company", string="Company",
    default=lambda self: self.env.company, required=True
)
    active = fields.Boolean(string="Active", default=True)
    date_planned = fields.Datetime(string="Planned Date")
    date_start = fields.Datetime(string="Start Date")
    date_end = fields.Datetime(string="End Date")
    duration = fields.Float(
    string="Intervention Duration (hours)", compute="_compute_duration",
    store=True, digits=(6, 2))
    line_ids = fields.One2many(
        "service.intervention.line", "intervention_id",
        string="Consumed Parts")
    observations = fields.Text(string="Observations")
    state = fields.Selection([
        ("draft", "Draft"),
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("done", "Completed"),
        ("invoiced", "Invoiced"),
    ], string="Status", default="draft", required=True, tracking=True)
    amount_parts = fields.Monetary(string="Parts Cost", currency_field="currency_id", compute="_compute_amount_parts", store=True)
    internal_cost = fields.Monetary(string="Internal Cost", currency_field="currency_id",groups="bsw_service.group_service_manager")
    currency_id = fields.Many2one("res.currency", string="Currency",related="company_id.currency_id", store=True, readonly=True)
    invoice_id = fields.Many2one(
        "account.move",  string="Facture",
    domain="[('move_type', '=', 'out_invoice')]"
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
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

    @api.depends("warranty_end_date")
    def _compute_is_under_warranty(self):
     today = fields.Date.today()
     for equipment in self:
         equipment.is_under_warranty = bool(
            equipment.warranty_end_date and equipment.warranty_end_date >= today
        )

    def action_plan(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only a draft intervention can be planned.")
        if not self.technician_id:
            raise UserError("A technician is required to plan an intervention.")
        self.state = "planned"

    def action_start(self):
        self.ensure_one()
        if self.state != "planned":
            raise UserError("Only a planned intervention can be started.")
        self.date_start = fields.Datetime.now()
        self.state = "in_progress"

    def action_done(self):
        self.ensure_one()
        if self.state != "in_progress":
            raise UserError("Only an ongoing intervention can be completed.")
        self.date_end = fields.Datetime.now()
        self.state = "done"
        template = self.env.ref("bsw_service.mail_template_intervention_done", raise_if_not_found=False)
        if template and self.partner_id.email:
            template.send_mail(self.id, force_send=True)

    def action_invoice(self):
        self.ensure_one()
        if self.state != "done":
            raise UserError("Only a completed intervention can be invoiced.")
        self.state = "invoiced"

    def action_reset_draft(self):
        self.ensure_one()
        if self.state == "invoiced":
            raise UserError("An invoiced intervention cannot be reset to draft.")
        self.state = "draft"

    @api.constrains("state", "technician_id")
    def _check_technician_exists(self):
        for intervention in self:
            if intervention.state != "draft" and not intervention.technician_id:
                raise UserError("An intervention requires a technician once it is no longer in draft.")

    @api.constrains("date_start","date_end")
    def _check_dates(self):
        for intervention in self:
            if intervention.date_start and intervention.date_end and intervention.date_start > intervention.date_end:
                raise UserError("The end date cannot be earlier than the start date.")

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
                raise UserError("An invoiced intervention cannot be deleted.")               


    def _cron_alert_overdue_interventions(self):
     from datetime import timedelta

     threshold = fields.Datetime.now() - timedelta(hours=48)

     overdue = self.search([
        ("state", "=", "planned"),
        ("date_planned", "<=", threshold),
    ])

     for intervention in overdue:
        if (not intervention.technician_id
            or not intervention.technician_id.team_id):
            continue

        manager = intervention.technician_id.team_id.manager_id

        if not manager or not manager.user_id:
            continue

        already_alerted = self.env["mail.activity"].search_count([
            ("res_model", "=", "service.intervention"),
            ("res_id", "=", intervention.id),
            (
                "activity_type_id",
                "=",
                self.env.ref("mail.mail_activity_data_todo").id,
            ),
            ("user_id", "=", manager.user_id.id),
        ])

        if already_alerted:
            continue

        intervention.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Intervention en retard",
            note=(
                "Intervention %s has been planned for more than 48 hours"
                "without being started."
            ) % intervention.name,
            user_id=manager.user_id.id,
        )        