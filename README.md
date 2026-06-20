# Odoo 19 TVA Sénégal

Addon Odoo 19 Enterprise pour le contrôle de conformité et l'impression de la
déclaration de TVA au Sénégal.

Le dépôt contient le module `l10n_sn_vat_compliance`, qui complète les modules
standards `l10n_sn` et `l10n_sn_reports`.

Fonctions principales :

- contrôle documentaire des factures fournisseurs ;
- suivi du NINEA et de la déductibilité ;
- synthèse de TVA collectée et déductible ;
- export CSV de la piste d'audit ;
- impression PDF du formulaire DGID/eTax en deux pages ;
- talon de paiement et références fiscales sénégalaises.

## Installation

Copier `l10n_sn_vat_compliance` dans un chemin déclaré dans `addons_path`,
actualiser la liste des applications, puis installer :

**Sénégal - Contrôle de conformité TVA**

## Dépendances

- Odoo 19 Enterprise ;
- `l10n_sn_reports` ;
- `wkhtmltopdf` avec Qt patché pour l'impression PDF.

## Auteur

MMLY

## Avertissement

Le module assiste la préparation et le contrôle de la déclaration. La
qualification fiscale et le dépôt auprès de la DGID doivent être validés selon
la réglementation et les procédures eTax en vigueur.
