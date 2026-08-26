from odoo import fields, models


class ServiceEquipment(models.Model):
    _name = "service.equipment"
    _description = "Équipement client"
    _order = "name"

    name = fields.Char(string="Désignation", required=True)
    active = fields.Boolean(string="Actif", default=True)
    partner_id = fields.Many2one(
        "res.partner", string="Client",
        required=True, ondelete="cascade"
    )
    serial_number = fields.Char(string="Numéro de série")
    model_reference = fields.Char(string="Référence modèle")
    installation_date = fields.Date(string="Date d'installation")
    intervention_ids = fields.One2many(
        "service.intervention", "equipment_id",
        string="Interventions"
    )
    intervention_count = fields.Integer(
        string="Nombre d'interventions",
        compute="_compute_intervention_count"
    )

    def _compute_intervention_count(self):
        for equip in self:
            equip.intervention_count = len(equip.intervention_ids)