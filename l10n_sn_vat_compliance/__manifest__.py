{
    "name": "Sénégal - Contrôle de conformité TVA",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Contrôle des pièces et piste d'audit pour la déclaration de TVA sénégalaise",
    "description": """
Extension de la localisation comptable sénégalaise d'Odoo 19 Enterprise.

Le module complète l10n_sn et l10n_sn_reports avec :
- les informations NINEA des partenaires ;
- le suivi des justificatifs de déduction sur les factures fournisseurs ;
- un contrôle périodique de la TVA collectée et déductible ;
- un export CSV détaillé pour la revue de la déclaration.
    """,
    "author": "MMLY",
    "license": "LGPL-3",
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
