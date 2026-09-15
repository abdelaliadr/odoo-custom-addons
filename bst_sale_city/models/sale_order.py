from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    city_id = fields.Many2one(
        comodel_name='res.city',
        string='City',
        domain="[('country_id', '=', partner_country_id)]",
        help="Customer's city, automatically transferred from the customer "
             "record and manually editable on the quotation. Any "
             "modification here never updates the customer record.",
    )
    partner_country_id = fields.Many2one(
        comodel_name='res.country',
        related='partner_id.country_id',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_city(self):
        """Transfers the customer's city to the quotation when the
        customer is selected, and updates it if the customer changes while
        the quotation is still in draft. This only applies in the
        customer -> quotation direction, never the reverse."""
        for order in self:
            order.city_id = order.partner_id.city_id

    def action_confirm(self):
        """Blocks confirmation until the city is filled in, with an
        explicit message. The quotation remains in draft."""
        orders_without_city = self.filtered(lambda order: not order.city_id)
        if orders_without_city:
            raise UserError(
                "Please enter the city before confirming the quotation %s."
                % ', '.join(orders_without_city.mapped('name'))
            )
        return super().action_confirm()
