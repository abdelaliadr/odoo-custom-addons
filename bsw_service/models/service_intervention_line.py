from odoo import api, fields, models


class ServiceInterventionLine(models.Model):
    _name = "service.intervention.line"
    _description = "Part consumed during an intervention"
    _order = "id"

    intervention_id = fields.Many2one(
        "service.intervention", string="Intervention",
        required=True, ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product", string="Product",
        required=True, ondelete="restrict"
    )
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    price_unit = fields.Monetary(string="Unit Price")
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        related="intervention_id.company_id.currency_id",
        store=True, readonly=True
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
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