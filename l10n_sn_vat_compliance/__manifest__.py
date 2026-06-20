{
    "name": "Senegal VAT Compliance",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Senegal VAT compliance, audit trail and DGID/eTax PDF declaration",
    "description": """
Extension for the Senegal accounting localization in Odoo 19 Enterprise.

The module extends l10n_sn and l10n_sn_reports with:
- partner NINEA information;
- deductible VAT supporting documents on vendor bills;
- periodic controls of collected and deductible VAT;
- detailed CSV audit exports;
- the operational DGID/eTax VAT declaration in PDF.
    """,
    "author": "MMLY",
    "website": "https://github.com/Tapha-git/Odoo_19_tva",
    "support": "Tapha-git@users.noreply.github.com",
    "license": "OPL-1",
    "price": 99.0,
    "currency": "EUR",
    "images": [
        "static/description/banner.png",
    ],
    "depends": [
        "l10n_sn_reports",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/account_move_views.xml",
        "wizard/vat_audit_views.xml",
        "report/vat_declaration_report.xml",
    ],
    "installable": True,
    "application": False,
}
