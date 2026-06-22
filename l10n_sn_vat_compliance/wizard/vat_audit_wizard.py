import base64
import csv
import io

from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class SenegalVatAuditWizard(models.TransientModel):
    _name = "l10n_sn.vat.audit.wizard"
    _description = "Contrôle de déclaration TVA Sénégal"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
    )
    date_from = fields.Date(
        string="Du",
        required=True,
        default=lambda self: fields.Date.start_of(
            fields.Date.context_today(self) - relativedelta(months=1), "month"
        ),
    )
    date_to = fields.Date(
        string="Au",
        required=True,
        default=lambda self: fields.Date.end_of(
            fields.Date.context_today(self) - relativedelta(months=1), "month"
        ),
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    collected_vat = fields.Monetary(
        string="TVA collectée comptabilisée",
        currency_field="currency_id",
        readonly=True,
    )
    booked_deductible_vat = fields.Monetary(
        string="TVA déductible comptabilisée",
        currency_field="currency_id",
        readonly=True,
    )
    eligible_deductible_vat = fields.Monetary(
        string="TVA déductible contrôlée",
        currency_field="currency_id",
        readonly=True,
    )
    estimated_balance = fields.Monetary(
        string="Solde estimé après contrôle",
        currency_field="currency_id",
        readonly=True,
    )
    anomaly_count = fields.Integer(
        string="Pièces à vérifier",
        readonly=True,
    )
    document_number = fields.Char(string="N° document eTax")
    submission_number = fields.Char(string="N° soumission")
    submitted_date = fields.Date(string="Date de soumission")
    previous_form_credit = fields.Monetary(
        string="Crédit du mois précédent (formulaire)",
        currency_field="currency_id",
    )
    line_ids = fields.One2many(
        comodel_name="l10n_sn.vat.audit.line",
        inverse_name="wizard_id",
        string="Détail",
        readonly=True,
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise UserError(_("La date de début doit précéder la date de fin."))

    def action_compute(self):
        self.ensure_one()
        if self.company_id.account_fiscal_country_id.code != "SN":
            raise UserError(
                _("La société sélectionnée doit utiliser le pays fiscal Sénégal.")
            )

        tax_lines = self.env["account.move.line"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("move_id.state", "=", "posted"),
                ("move_id.date", ">=", self.date_from),
                ("move_id.date", "<=", self.date_to),
                (
                    "move_id.move_type",
                    "in",
                    ("out_invoice", "out_refund", "out_receipt",
                     "in_invoice", "in_refund", "in_receipt"),
                ),
                ("tax_line_id", "!=", False),
                ("tax_line_id.type_tax_use", "in", ("sale", "purchase")),
                ("tax_line_id.amount", "in", (10.0, 18.0)),
            ],
            order="date, move_id, id",
        )

        commands = [Command.clear()]
        collected = 0.0
        booked_deductible = 0.0
        eligible_deductible = 0.0
        anomalous_moves = set()

        for tax_line in tax_lines:
            move = tax_line.move_id
            is_sale = move.is_sale_document(include_receipts=True)
            # Sales tax lines are credited on invoices and debited on refunds.
            # Purchase tax lines follow the opposite sign convention. Normalizing
            # by operation type preserves refunds as negative amounts.
            normalized_tax = -tax_line.balance if is_sale else tax_line.balance
            normalized_base = (
                -tax_line.tax_base_amount if is_sale else tax_line.tax_base_amount
            )
            issues = [] if is_sale else move._sn_vat_compliance_issues()

            if is_sale:
                collected += normalized_tax
                control_state = "compliant"
            else:
                booked_deductible += normalized_tax
                if move.sn_vat_deduction_status == "excluded":
                    control_state = "excluded"
                elif issues:
                    control_state = "to_review"
                    anomalous_moves.add(move.id)
                else:
                    control_state = "compliant"
                    eligible_deductible += normalized_tax

            commands.append(
                Command.create(
                    {
                        "move_id": move.id,
                        "operation_type": "sale" if is_sale else "purchase",
                        "tax_name": tax_line.tax_line_id.display_name,
                        "tax_rate": abs(tax_line.tax_line_id.amount),
                        "base_amount": normalized_base,
                        "tax_amount": normalized_tax,
                        "control_state": control_state,
                        "issue_summary": " ; ".join(issues)
                        or (
                            move.sn_vat_exclusion_reason
                            if control_state == "excluded"
                            else False
                        ),
                    }
                )
            )

        self.write(
            {
                "line_ids": commands,
                "collected_vat": collected,
                "booked_deductible_vat": booked_deductible,
                "eligible_deductible_vat": eligible_deductible,
                "estimated_balance": collected - eligible_deductible,
                "anomaly_count": len(anomalous_moves),
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_export_csv(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Lancez d'abord le contrôle TVA."))

        stream = io.StringIO(newline="")
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(
            [
                "Date comptable",
                "Date facture",
                "Type",
                "Pièce",
                "Partenaire",
                "NINEA",
                "Référence",
                "Taxe",
                "Taux",
                "Base XOF",
                "TVA XOF",
                "Contrôle",
                "Anomalies",
            ]
        )
        state_labels = dict(
            self.env["l10n_sn.vat.audit.line"]._fields["control_state"].selection
        )
        operation_labels = dict(
            self.env["l10n_sn.vat.audit.line"]._fields["operation_type"].selection
        )
        for line in self.line_ids:
            move = line.move_id
            partner = move.partner_id.commercial_partner_id
            writer.writerow(
                [
                    move.date,
                    move.invoice_date or "",
                    operation_labels.get(line.operation_type),
                    move.name,
                    partner.display_name,
                    partner.sn_ninea or partner.vat or "",
                    move.ref or "",
                    line.tax_name,
                    line.tax_rate,
                    line.base_amount,
                    line.tax_amount,
                    state_labels.get(line.control_state),
                    line.issue_summary or "",
                ]
            )

        filename = "controle_tva_sn_%s_%s.csv" % (self.date_from, self.date_to)
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": base64.b64encode(stream.getvalue().encode("utf-8-sig")),
                "mimetype": "text/csv",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=1" % attachment.id,
            "target": "self",
        }

    def _get_dgid_form_values(self):
        """Return the official DGID line layout from Odoo's Senegal tax report."""
        self.ensure_one()
        report = self.env.ref("l10n_sn.account_tax_report_sn").with_company(
            self.company_id
        )
        options = report.get_options(
            {
                "date": {
                    "date_from": fields.Date.to_string(self.date_from),
                    "date_to": fields.Date.to_string(self.date_to),
                    "filter": "custom",
                    "mode": "range",
                },
                "companies": [
                    {
                        "id": self.company_id.id,
                        "name": self.company_id.name,
                        "selected": True,
                    }
                ],
            }
        )
        values_by_code = {}
        for report_line in report._get_lines(options):
            report_line_id = next(
                (
                    column.get("report_line_id")
                    for column in report_line.get("columns", [])
                    if column.get("report_line_id")
                ),
                False,
            )
            if not report_line_id:
                continue
            code = self.env["account.report.line"].browse(report_line_id).code
            if not code:
                continue
            values_by_code[code] = {
                column.get("expression_label"): column.get("no_format") or 0.0
                for column in report_line.get("columns", [])
            }

        def amount(code, label="tax"):
            return values_by_code.get(code, {}).get(label, 0.0)

        report_has_values = any(
            value
            for expressions in values_by_code.values()
            for value in expressions.values()
        )
        fallback = self._get_dgid_fallback_values() if not report_has_values else {}

        def report_or_fallback(code, label, form_line):
            return amount(code, label) if report_has_values else fallback.get(form_line, 0.0)

        prepayment = amount("SN_PREPAY")
        import_tax = amount("SN_IMPORT")
        domestic_tax = amount("SN_DOMESTIC")
        reimbursement = amount("SN_REIMBURSEMENT_ACCEPTED")
        prior_credit = amount("SN_CREDIT")
        gross_vat = amount("SN_TAXABLE")
        current_deductions = prepayment + import_tax + domestic_tax

        return {
            "period_label": format_date(
                self.env, self.date_from, date_format="MMMM yyyy"
            ).upper(),
            "period_label_lower": format_date(
                self.env, self.date_from, date_format="MMMM yyyy"
            ),
            "date_from_label": format_date(
                self.env, self.date_from, date_format="dd MMMM yyyy"
            ),
            "date_to_label": format_date(
                self.env, self.date_to, date_format="dd MMMM yyyy"
            ),
            "deadline_date": self.date_to + relativedelta(days=15),
            "deadline_label": format_date(
                self.env,
                self.date_to + relativedelta(days=15),
                date_format="dd MMMM yyyy",
            ),
            "line_5": report_or_fallback("SN_OPE", "base", "line_5"),
            "line_10": report_or_fallback("SN_Export", "base", "line_10"),
            "line_15": report_or_fallback("SN_NON_TAXED", "base", "line_15"),
            "line_20": report_or_fallback("SN_SUSPENSION", "base", "line_20"),
            "line_25": (
                amount("SN_Export", "base")
                + amount("SN_NON_TAXED", "base")
                + amount("SN_SUSPENSION", "base")
                + amount("SN_EXEMPT", "base")
            ) if report_has_values else fallback.get("line_25", 0.0),
            "line_30": report_or_fallback("SN_SELF", "base", "line_30"),
            "line_35": report_or_fallback("SN_TAXABLE", "base", "line_35"),
            "line_40": report_or_fallback("SN_TAXABLE_10", "base", "line_40"),
            "line_45": report_or_fallback("SN_TAXABLE_18", "base", "line_45"),
            "line_50": report_or_fallback("SN_TAXABLE_10", "tax", "line_50"),
            "line_55": report_or_fallback("SN_TAXABLE_18", "tax", "line_55"),
            "line_60": gross_vat if report_has_values else fallback.get("line_60", 0.0),
            "line_65": report_or_fallback("SN_WITHHOLDING", "base", "line_65"),
            "line_70": report_or_fallback("SN_WITHHOLDING", "tax", "line_70"),
            "line_75": report_or_fallback("SN_DDI", "tax", "line_75"),
            "line_76": prepayment if report_has_values else fallback.get("line_76", 0.0),
            "line_80": report_or_fallback("SN_IMPORT", "base", "line_80"),
            "line_85": import_tax if report_has_values else fallback.get("line_85", 0.0),
            "line_90": domestic_tax if report_has_values else fallback.get("line_90", 0.0),
            "line_91": (
                import_tax + domestic_tax
                if report_has_values
                else fallback.get("line_91", 0.0)
            ),
            "line_92": (
                current_deductions
                if report_has_values
                else fallback.get("line_92", 0.0)
            ),
            "line_93": (
                max(gross_vat - current_deductions, 0.0)
                if report_has_values
                else fallback.get("line_93", 0.0)
            ),
            "line_95": reimbursement if report_has_values else fallback.get("line_95", 0.0),
            "line_96": self.previous_form_credit,
            "line_100": prior_credit if report_has_values else fallback.get("line_100", 0.0),
            "line_105": (
                current_deductions + reimbursement + prior_credit
                if report_has_values
                else fallback.get("line_105", 0.0)
            ),
            "line_110": report_or_fallback("SN_DUE", "tax", "line_110"),
            "line_115": report_or_fallback("SN_REPORT", "tax", "line_115"),
            "line_120": report_or_fallback(
                "SN_REIMBURSEMENT_REVIEW", "tax", "line_120"
            ),
        }

    def _get_dgid_fallback_values(self):
        """Build DGID amounts from audited entries when fiscal tags are absent."""
        self.ensure_one()
        values = {"line_%s" % number: 0.0 for number in (
            5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75,
            76, 80, 85, 90, 91, 92, 93, 95, 100, 105, 110, 115, 120,
        )}

        for line in self.line_ids:
            taxable_base = (
                line.tax_amount * 100.0 / line.tax_rate
                if line.tax_rate
                else line.base_amount
            )
            if line.operation_type == "sale":
                values["line_5"] += taxable_base
                values["line_35"] += taxable_base
                if line.tax_rate == 10.0:
                    values["line_40"] += taxable_base
                    values["line_50"] += line.tax_amount
                elif line.tax_rate == 18.0:
                    values["line_45"] += taxable_base
                    values["line_55"] += line.tax_amount
                values["line_60"] += line.tax_amount
                continue

            if line.control_state != "compliant":
                continue
            move = line.move_id
            if move.sn_vat_document_type == "import":
                values["line_80"] += taxable_base
                values["line_85"] += line.tax_amount
            elif move.sn_vat_document_type == "withholding":
                values["line_65"] += taxable_base
                values["line_70"] += line.tax_amount
            else:
                values["line_90"] += line.tax_amount

        values["line_76"] = values["line_70"] + values["line_75"]
        values["line_91"] = values["line_85"] + values["line_90"]
        values["line_92"] = values["line_76"] + values["line_91"]
        values["line_93"] = max(values["line_60"] - values["line_92"], 0.0)
        values["line_105"] = (
            values["line_92"] + values["line_95"] + values["line_100"]
        )
        values["line_110"] = max(values["line_60"] - values["line_105"], 0.0)
        values["line_115"] = max(values["line_105"] - values["line_60"], 0.0)
        return values

    def action_print_dgid_vat_declaration(self):
        self.ensure_one()
        if not self.line_ids:
            self.action_compute()
        return self.env.ref(
            "l10n_sn_vat_compliance.action_report_dgid_vat_declaration"
        ).report_action(self)


class SenegalVatAuditLine(models.TransientModel):
    _name = "l10n_sn.vat.audit.line"
    _description = "Ligne de contrôle TVA Sénégal"
    _order = "move_date, move_id, id"

    wizard_id = fields.Many2one(
        comodel_name="l10n_sn.vat.audit.wizard",
        required=True,
        ondelete="cascade",
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Pièce",
        required=True,
        readonly=True,
    )
    move_date = fields.Date(
        related="move_id.date",
        string="Date",
        store=True,
    )
    partner_id = fields.Many2one(
        related="move_id.partner_id",
        string="Partenaire",
        store=True,
    )
    operation_type = fields.Selection(
        selection=[
            ("sale", "TVA collectée"),
            ("purchase", "TVA déductible"),
        ],
        string="Type",
        required=True,
        readonly=True,
    )
    tax_name = fields.Char(
        string="Taxe",
        readonly=True,
    )
    tax_rate = fields.Float(
        string="Taux (%)",
        readonly=True,
    )
    currency_id = fields.Many2one(
        related="wizard_id.currency_id",
    )
    base_amount = fields.Monetary(
        string="Base",
        currency_field="currency_id",
        readonly=True,
    )
    tax_amount = fields.Monetary(
        string="TVA",
        currency_field="currency_id",
        readonly=True,
    )
    control_state = fields.Selection(
        selection=[
            ("compliant", "Conforme"),
            ("to_review", "À vérifier"),
            ("excluded", "Non déductible"),
        ],
        string="Contrôle",
        readonly=True,
    )
    issue_summary = fields.Char(
        string="Anomalies / motif",
        readonly=True,
    )
