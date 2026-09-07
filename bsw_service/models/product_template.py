from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_spare_part = fields.Boolean(
        string="Spare Part",
        help="Product that can be used as a spare part during an intervention.",
        default=False,
    )