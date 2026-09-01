from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            order._create_service_intervention()
        return result

    def _create_service_intervention(self):
        self.ensure_one()
        spare_lines = self.order_line.filtered(
            lambda line: line.product_id.is_spare_part)
        if not spare_lines:
         return
        intervention = self.env["service.intervention"].create({
        "partner_id": self.partner_id.id,
        })
        for line in spare_lines:
         self.env["service.intervention.line"].create({
            "intervention_id": intervention.id,
            "product_id": line.product_id.id,
            "quantity": line.product_uom_qty,
            "price_unit": line.price_unit
        })