from odoo import api, fields, models


class ServiceInterventionLine(models.Model):
    _name = "service.intervention.line"
    _description = "Pièce consommée sur une intervention"
    _order = "id"

    intervention_id = fields.Many2one(
        "service.intervention", string="Intervention",
        required=True, ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product", string="Produit",
        required=True, ondelete="restrict"
    )
    quantity = fields.Float(string="Quantité", default=1.0, required=True)
    price_unit = fields.Monetary(string="Prix unitaire")
    currency_id = fields.Many2one(
        "res.currency", string="Devise",
        related="intervention_id.company_id.currency_id",
        store=True, readonly=True
    )
    price_subtotal = fields.Monetary(
        string="Sous-total",
        compute="_compute_price_subtotal", store=True
    )

    @api.depends("quantity", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.standard_price