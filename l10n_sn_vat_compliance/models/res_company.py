from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sn_tax_account = fields.Char(string="Compte d'impôt")
    sn_tax_division = fields.Char(string="Division fiscale")
    sn_collection_location = fields.Char(string="Lieu de perception")
    sn_tax_establishment = fields.Char(string="Établissement fiscal")
    sn_taxable_object = fields.Char(string="Objet imposable")
