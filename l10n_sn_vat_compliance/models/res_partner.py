from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sn_ninea = fields.Char(
        string="NINEA",
        index=True,
        help="Numéro d'Identification Nationale des Entreprises et Associations.",
    )
