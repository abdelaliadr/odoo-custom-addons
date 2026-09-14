from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    city_id = fields.Many2one(
        comodel_name='res.city',
        string='City',
        domain="[('country_id', '=', partner_country_id)]",
        help="Ville du client, reportée automatiquement depuis la fiche "
             "client et modifiable manuellement sur le devis. Une "
             "modification ici ne met jamais à jour la fiche du client.",
    )
    partner_country_id = fields.Many2one(
        comodel_name='res.country',
        related='partner_id.country_id',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_city(self):
        """reporte la ville du client sur le devis à la
        sélection du client, et la met à jour si le client change tant que
        le devis est en brouillon.Ceci ne s'applique que dans le
        sens client -> devis, jamais l'inverse."""
        for order in self:
            order.city_id = order.partner_id.city_id

    def action_confirm(self):
        """bloque la confirmation tant que la ville n'est pas
        renseignée, avec un message explicite. Le devis reste en brouillon."""
        orders_without_city = self.filtered(lambda order: not order.city_id)
        if orders_without_city:
            raise UserError(
    "Veuillez renseigner la ville avant de confirmer le devis %s."
    % ', '.join(orders_without_city.mapped('name'))
)
        return super().action_confirm()            

