from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_spare_part = fields.Boolean(
        string="Pièce détachée",
        help="Produit utilisable comme pièce détachée sur une intervention.",
        default=False,
    )