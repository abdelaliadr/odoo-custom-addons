# BSW Service & Interventions

Module personnalisé Odoo 19 destiné à la gestion des interventions techniques, des techniciens, des équipes, des équipements clients, des contrats de service et des pièces détachées.

## Présentation

**BSW Service & Interventions** permet de gérer le cycle de vie complet des interventions techniques.

Le module permet notamment de :

* Gérer les interventions techniques
* Affecter les interventions aux techniciens
* Organiser les techniciens en équipes
* Gérer les équipements des clients
* Gérer les contrats de service
* Suivre les pièces détachées consommées
* Calculer la durée des interventions et le coût des pièces
* Suivre l'état des interventions
* Générer des alertes pour les interventions en retard
* Consulter les interventions depuis les fiches clients
* Gérer les droits d'accès selon les rôles des utilisateurs

## Fonctionnalités

### Interventions

Le module permet de gérer les interventions selon un workflow complet :

```text
Brouillon → Planifiée → En cours → Terminée → Facturée
```

Chaque intervention peut contenir :

* Client
* Équipement
* Technicien
* Contrat
* Date planifiée
* Date de début
* Date de fin
* Durée de l'intervention
* Pièces consommées
* Coût des pièces
* Coût interne
* Observations
* Facture
* Statut

### Techniciens

Les techniciens peuvent être créés et associés à un utilisateur Odoo.

Chaque technicien possède notamment :

* Nom
* Utilisateur Odoo lié
* Équipe
* Téléphone
* Interventions associées

Le module affiche également le nombre d'interventions associées à chaque technicien.

### Équipes techniques

Les techniciens peuvent être organisés en équipes.

Chaque équipe possède :

* Nom de l'équipe
* Responsable
* Techniciens
* Nombre de techniciens

Le responsable d'une équipe peut accéder aux interventions affectées aux techniciens de son équipe.

### Équipements clients

Le module permet d'enregistrer et de suivre les équipements appartenant aux clients.

Les informations disponibles comprennent :

* Nom
* Client
* Numéro de série
* Référence modèle
* Date d'installation
* Date de fin de garantie
* Statut de garantie
* Interventions associées

Les équipements sont automatiquement filtrés en fonction du client sélectionné.

### Contrats de service

Les contrats de service peuvent être créés pour les clients et associés aux produits couverts.

Les types de contrats disponibles sont :

* Standard
* Premium
* Urgence 24/7

Un contrat contient notamment :

* Client
* Type de contrat
* Date de début
* Date de fin
* Produits couverts
* Interventions associées

### Pièces détachées

Le module permet d'enregistrer les pièces détachées consommées pendant une intervention.

Pour chaque pièce, il est possible de renseigner :

* Produit
* Quantité
* Prix unitaire
* Sous-total

Le coût total des pièces est automatiquement calculé au niveau de l'intervention.

Les produits peuvent également être identifiés comme **pièces détachées**.

### Alertes des interventions en retard

Une action planifiée vérifie les interventions qui :

* Sont toujours à l'état **Planifiée**
* Sont planifiées depuis plus de 48 heures
* N'ont pas encore commencé

Une activité est automatiquement créée pour le responsable de l'équipe concernée.

### Sécurité et droits d'accès

Le module propose une gestion des accès basée sur les rôles.

Les principaux rôles sont :

* **Technicien**
* **Responsable de service**
* **Administrateur de service**

Le technicien peut accéder à ses propres interventions.

Le responsable peut accéder aux interventions des techniciens de son équipe.

L'administrateur peut accéder à l'ensemble des interventions.

## Installation

### Prérequis

* Odoo 19.0
* PostgreSQL
* Python 3
* Dépendances standard d'Odoo

### Installation du module

1. Copier le module dans l'un des répertoires d'addons Odoo.

Exemple :

```text
custom-addons/
└── bsw_service/
```

2. Vérifier que le répertoire contenant les addons personnalisés est présent dans la configuration Odoo :

```ini
addons_path = addons,C:\odoo-dev\custom-addons
```

3. Redémarrer le serveur Odoo.

4. Activer le **mode développeur**.

5. Aller dans :

**Applications → Mettre à jour la liste des applications**

6. Rechercher :

```text
BSW Service & Interventions
```

7. Cliquer sur **Installer**.

## Structure du module

```text
bsw_service/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── service_intervention.py
│   ├── service_intervention_line.py
│   ├── service_equipment.py
│   ├── service_contract.py
│   ├── service_team.py
│   ├── service_technician.py
│   └── res_partner.py
│
├── views/
│   ├── service_intervention_views.xml
│   ├── service_equipment_views.xml
│   ├── service_contract_views.xml
│   ├── service_team_views.xml
│   ├── service_technician_views.xml
│   └── res_partner_views.xml
│
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
│
├── data/
│   ├── sequence.xml
│   └── ...
│
├── report/
│   └── ...
│
├── i18n/
│   └── fr.po
│
└── static/
    └── src/
        └── scss/
            └── service_intervention.scss
```

## Traduction

Le code source du module utilise l'anglais comme langue principale.

Les traductions françaises sont disponibles dans :

```text
i18n/fr.po
```

Odoo charge automatiquement les fichiers de traduction présents dans le dossier `i18n`.

## Dépendances

Le module dépend des modules Odoo standards suivants :

```python
"base",
"mail",
"product",
"sale",
"account",
```

## Informations techniques

| Information  |      Valeur          |
| ------------ | ---------------------|
| Module       | `bsw_service`        |
| Version      | `19.0.1.0.0`         |
| Version Odoo | `19.0`               |
| Catégorie    | Services             |
| Licence      | LGPL-3               |
| Auteur       | Blackswan Technology |

## Développement

Pour le développement, il est recommandé d'utiliser la branche `dev`.

Pour commencer à travailler sur cette branche :

```bash
git checkout dev
```

Après avoir effectué des modifications :

```bash
git add .
git commit -m "[TYPE]: description"
```

Exemple :

```bash
git commit -m "[FEAT]: add service contract management"
```

Puis envoyer les commits vers le dépôt distant :

```bash
git push origin dev
```

La branche `master` est réservée aux versions stables du projet.

### Exemples

```text
[FEAT]: add service contracts
[FIX]: fix intervention validation
[IMP]: improve service report layout
[REFACTOR]: simplify intervention model
[DOCS]: update README
```

## Workflow d'une intervention

Le cycle de vie d'une intervention est le suivant :

```text
                    ┌─────────────┐
                    │  Brouillon  │
                    └──────┬──────┘
                           │ Planifier
                           ▼
                    ┌─────────────┐
                    │  Planifiée  │
                    └──────┬──────┘
                           │ Démarrer
                           ▼
                    ┌─────────────┐
                    │   En cours  │
                    └──────┬──────┘
                           │ Terminer
                           ▼
                    ┌─────────────┐
                    │  Terminée   │
                    └──────┬──────┘
                           │ Facturer
                           ▼
                    ┌─────────────┐
                    │   Facturée  │
                    └─────────────┘
```

## Bon d'intervention

Le module permet également de gérer les informations nécessaires à la génération d'un **bon d'intervention / rapport d'intervention** contenant les principales informations liées à l'intervention technique.

## Auteur

**Blackswan Technology**

## Licence

Ce module est distribué sous licence **LGPL-3**.
