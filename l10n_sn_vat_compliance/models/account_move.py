from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sn_is_senegal_company = fields.Boolean(
        compute="_compute_sn_is_senegal_company",
    )
    sn_vat_document_type = fields.Selection(
        selection=[
            ("local_invoice", "Facture locale"),
            ("import", "Importation / document douanier"),
            ("withholding", "Précompte / retenue"),
            ("other", "Autre justificatif"),
        ],
        string="Type de justificatif TVA",
        default="local_invoice",
        tracking=True,
    )
    sn_vat_deduction_status = fields.Selection(
        selection=[
            ("to_review", "À vérifier"),
            ("eligible", "Déductible"),
            ("excluded", "Non déductible"),
        ],
        string="Déductibilité TVA",
        default="to_review",
        tracking=True,
    )
    sn_customs_reference = fields.Char(
        string="Référence douanière / DDI",
        tracking=True,
    )
    sn_vat_supporting_reference = fields.Char(
        string="Référence justificatif TVA",
        tracking=True,
    )
    sn_vat_exclusion_reason = fields.Char(
        string="Motif de non-déduction",
        tracking=True,
    )
    sn_vat_compliance_state = fields.Selection(
        selection=[
            ("not_applicable", "Non applicable"),
            ("to_review", "À vérifier"),
            ("compliant", "Conforme"),
            ("excluded", "Exclue"),
        ],
        string="Contrôle TVA Sénégal",
        compute="_compute_sn_vat_compliance",
    )
    sn_vat_compliance_message = fields.Text(
        string="Points de contrôle TVA",
        compute="_compute_sn_vat_compliance",
    )

    @api.depends("company_id.account_fiscal_country_id.code")
    def _compute_sn_is_senegal_company(self):
        for move in self:
            move.sn_is_senegal_company = (
                move.company_id.account_fiscal_country_id.code == "SN"
            )

    def _sn_has_deductible_vat(self):
        self.ensure_one()
        return any(
            line.tax_line_id
            and line.tax_line_id.type_tax_use == "purchase"
            and abs(line.tax_line_id.amount) in (10.0, 18.0)
            for line in self.line_ids
        )

    def _sn_vat_compliance_issues(self):
        self.ensure_one()
        if (
            not self.sn_is_senegal_company
            or self.move_type not in ("in_invoice", "in_refund", "in_receipt")
            or not self._sn_has_deductible_vat()
            or self.sn_vat_deduction_status == "excluded"
        ):
            return []

        issues = []
        commercial_partner = self.partner_id.commercial_partner_id
        if not (commercial_partner.sn_ninea or commercial_partner.vat):
            issues.append("NINEA / identifiant fiscal du fournisseur manquant")
        if not self.ref:
            issues.append("référence de facture fournisseur manquante")
        if not self.invoice_date:
            issues.append("date de facture manquante")
        if not self.attachment_ids:
            issues.append("copie du justificatif non jointe")
        if self.sn_vat_document_type == "import" and not self.sn_customs_reference:
            issues.append("référence douanière ou DDI manquante")
        if self.sn_vat_deduction_status == "to_review":
            issues.append("déductibilité non encore validée")
        return issues

    @api.depends(
        "company_id.account_fiscal_country_id.code",
        "move_type",
        "line_ids.tax_line_id",
        "partner_id",
        "partner_id.sn_ninea",
        "partner_id.commercial_partner_id.sn_ninea",
        "partner_id.vat",
        "partner_id.commercial_partner_id.vat",
        "ref",
        "invoice_date",
        "attachment_ids",
        "sn_vat_document_type",
        "sn_vat_deduction_status",
        "sn_customs_reference",
        "sn_vat_exclusion_reason",
    )
    def _compute_sn_vat_compliance(self):
        for move in self:
            if (
                not move.sn_is_senegal_company
                or move.move_type not in ("in_invoice", "in_refund", "in_receipt")
                or not move._sn_has_deductible_vat()
            ):
                move.sn_vat_compliance_state = "not_applicable"
                move.sn_vat_compliance_message = False
                continue

            if move.sn_vat_deduction_status == "excluded":
                move.sn_vat_compliance_state = "excluded"
                move.sn_vat_compliance_message = (
                    move.sn_vat_exclusion_reason or "TVA marquée comme non déductible."
                )
                continue

            issues = move._sn_vat_compliance_issues()
            move.sn_vat_compliance_state = "to_review" if issues else "compliant"
            move.sn_vat_compliance_message = (
                " ; ".join(issues) if issues else "Les contrôles documentaires sont satisfaits."
            )
