# Contrôle de conformité TVA Sénégal — Odoo 18

Développé et maintenu par **MMLY**.

Ce module complète le module standard `l10n_sn`, qui contient les lignes du
rapport de TVA sénégalais dans Odoo 18, ainsi que le moteur Enterprise
`account_reports`.
Il ne remplace pas la déclaration TVA standard d'Odoo : il ajoute une piste
d'audit documentaire avant validation et télédéclaration.

## Fonctions

- champ NINEA sur les partenaires ;
- qualification du justificatif et de la déductibilité sur les factures
  fournisseurs ;
- contrôle des références, dates, pièces jointes et documents douaniers ;
- synthèse mensuelle de la TVA collectée, comptabilisée comme déductible et
  contrôlée comme déductible ;
- traitement cohérent des factures et avoirs ;
- export CSV du détail de contrôle.

## Installation

1. Ajouter le dossier `custom_addons` au paramètre `addons_path`.
2. Installer la localisation Sénégal et vérifier que le pays fiscal de la
   société est **Sénégal**.
3. Actualiser la liste des applications.
4. Installer **Sénégal - Contrôle de conformité TVA**.
5. Ouvrir **Comptabilité > Analyse > Taxes & Fiscal > Contrôle TVA Sénégal**.

Exemple de chemin :

```ini
addons_path = C:\...\odoo\addons,C:\...\custom_addons
```

## Test sur Odoo.sh

1. Utiliser la branche Git `18.0` dans un staging Odoo.sh basé sur Odoo 18
   Enterprise.
2. Vérifier que **Sénégal - Comptabilité** (`l10n_sn`) et le moteur Enterprise
   **Accounting Reports** (`account_reports`) sont disponibles.
3. Dans le mode développeur, actualiser la liste des applications.
4. Rechercher puis installer **Senegal VAT Compliance**.
5. Tester le contrôle TVA et l'impression PDF avec une copie de la base avant
   toute utilisation fiscale réelle.

## Important

Le taux et les lignes de déclaration sont ceux de la localisation officielle
Odoo 18 Enterprise installée. La qualification juridique d'une opération, d'une
exonération ou d'un droit à déduction doit être validée par le responsable
fiscal ou le conseil de l'entreprise avant dépôt auprès de la DGID.

La DGID indique une échéance au plus tard le 15 du mois suivant pour le régime
normal, et le 15 de janvier, avril, juillet et octobre pour le régime du réel
simplifié. La périodicité doit donc être configurée selon le régime fiscal réel
de chaque société, et non déduite automatiquement par ce module.

## Références officielles consultées

- DGID, calendrier des déclarations à échéance mensuelle ou trimestrielle :
  https://www.dgid.sn/wp-content/uploads/2024/02/CALENDRIER-DECLARATION-MENSUELLE.pdf
- DGID, services de déclaration et paiement en ligne :
  https://www.dgid.sn/e-services/
- DGID, rapport sur les dépenses fiscales 2021 (taux normal de 18 % et taux
  réduit de 10 % pour les prestations d'hébergement et de restauration
  agréées) :
  https://www.dgid.sn/wp-content/uploads/2023/12/RAPPORT-DEVALUATION-BUDGETAIRES-DEPENSES-FISCALES-2021_compressed.pdf
