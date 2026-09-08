from odoo import fields, models, api


class ServiceEquipment(models.Model):
    _name = "service.equipment"
    _description = "Customer Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer",
        required=True, ondelete="cascade"
    )
    serial_number = fields.Char(string="Serial Number")
    model_reference = fields.Char(string="Model Reference")
    installation_date = fields.Date(string="Installation Date")
    intervention_ids = fields.One2many(
        "service.intervention", "equipment_id",
        string="Interventions"
    )
    intervention_count = fields.Integer(
        string="Number of Interventions",
        compute="_compute_intervention_count"
    )
    warranty_end_date = fields.Date(string="Warranty End Date")
    is_under_warranty = fields.Boolean(
        string="Under Warranty", compute="_compute_is_under_warranty")

    @api.depends("intervention_ids")
    def _compute_intervention_count(self):
        for equip in self:
            equip.intervention_count = len(equip.intervention_ids)

    @api.depends("warranty_end_date")
    def _compute_is_under_warranty(self):
        today = fields.Date.today()
        for equipment in self:
             equipment.is_under_warranty = bool(
                equipment.warranty_end_date and equipment.warranty_end_date >= today)        