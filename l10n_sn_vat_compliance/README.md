# Contrôle de conformité TVA Sénégal — Odoo 19

Développé et maintenu par **MMLY**.

Ce module complète les modules standards `l10n_sn` et `l10n_sn_reports`.
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

## Important

Le taux et les lignes de déclaration sont ceux de la localisation officielle
Odoo 19 installée. La qualification juridique d'une opération, d'une
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
