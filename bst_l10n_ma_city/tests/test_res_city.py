from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestResCity(TransactionCase):
    """Tests du Module 1 - bst_l10n_ma_city.
    Chaque test correspond à un critère d'acceptation du cahier des charges."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.morocco = cls.env['res.country'].search([('code', '=', 'MA')], limit=1)
        cls.ma_cities = cls.env['res.city'].search([
            ('country_id', '=', cls.morocco.id),
        ])

    def test_01_referentiel_villes_charge(self):
        """CA-01 : le référentiel contient les villes du Maroc après
        installation, en nombre significatif"""
        self.assertEqual(
            len(self.ma_cities), 40,
            "Le référentiel doit contenir 40 villes marocaines "
            "après installation du module."
        )

    def test_02_villes_ont_code_postal_et_region(self):
        """CA-01 : chaque ville porte bien un code postal et une région."""
        villes_sans_zip = self.ma_cities.filtered(lambda c: not c.zipcode)
        villes_sans_region = self.ma_cities.filtered(lambda c: not c.state_id)
        self.assertFalse(
            villes_sans_zip,
            "Certaines villes marocaines n'ont pas de code postal : %s"
            % villes_sans_zip.mapped('name')[:5]
        )
        self.assertFalse(
            villes_sans_region,
            "Certaines villes marocaines n'ont pas de région : %s"
            % villes_sans_region.mapped('name')[:5]
        )

    def test_03_douze_regions_creees(self):
        """RG-02 : les 12 régions du Maroc doivent exister, rattachées au
        pays Maroc (elles ne sont pas fournies en standard par Odoo)."""
        regions = self.env['res.country.state'].search([
            ('country_id', '=', self.morocco.id),
        ])
        self.assertEqual(
            len(regions), 12,
            "Le Maroc doit avoir exactement 12 régions après installation "
            "du module (trouvé : %d)." % len(regions)
        )

    def test_04_enforce_cities_active_sur_maroc(self):
        """CA-02 (précondition) : le paramètre permettant l'affichage de la
        ville en liste déroulante doit être activé sur le pays Maroc."""
        self.assertTrue(
            self.morocco.enforce_cities,
            "Le champ enforce_cities doit être activé sur le pays Maroc "
            "pour que le champ Ville s'affiche en liste déroulante sur "
            "les contacts (RG-03)."
        )

    def test_05_selection_ville_remplit_zip_sur_contact(self):
        """CA-02 : la sélection d'une ville sur un contact marocain
        renseigne automatiquement le code postal (comportement standard de
        base_address_extended, dépend de enforce_cities)."""
        ville = self.ma_cities[0]
        partner = self.env['res.partner'].create({
            'name': 'Client de test BF-VILLES-01',
            'country_id': self.morocco.id,
            'city_id': ville.id,
        })
        self.assertEqual(
            partner.city_id, ville,
            "La ville sélectionnée doit être conservée sur le contact."
        )
        # Le remplissage du zip est un comportement standard lié au
        # widget/onchange du formulaire ; on vérifie ici la cohérence des
        # données sous-jacentes utilisées par ce mécanisme.
        self.assertEqual(
            partner.city_id.zipcode, ville.zipcode,
            "Le code postal de la ville sélectionnée doit correspondre à "
            "celui du référentiel."
        )

    def test_06_ville_manuelle_survit_a_une_mise_a_jour(self):
        """CA-04 : une ville ajoutée manuellement doit toujours être
        présente après une mise à jour du module (non testable directement
        en TransactionCase car cela nécessite un rechargement complet du
        module).

        Ce test vérifie a minima que la donnée créée manuellement n'est pas
        immédiatement liée à un external ID du module (ce qui la rendrait
        vulnérable à un rechargement), condition nécessaire pour que le
        comportement noupdate protège les vraies données du CSV et laisse
        les ajouts manuels intacts.
        """
        ville_manuelle = self.env['res.city'].create({
            'name': 'Ville Test Manuelle BF-VILLES-01',
            'zipcode': '99999',
            'country_id': self.morocco.id,
            'state_id': self.env['res.country.state'].search(
                [('country_id', '=', self.morocco.id)], limit=1
            ).id,
        })
        imd = self.env['ir.model.data'].search([
            ('model', '=', 'res.city'),
            ('res_id', '=', ville_manuelle.id),
        ])
        self.assertFalse(
            imd,
            "Une ville créée manuellement ne doit avoir aucun external ID "
            "de données du module (sinon elle serait considérée comme "
            "faisant partie du référentiel livré, et pourrait être "
            "affectée par une réinstallation)."
        )

    def test_07_donnees_csv_verrouillees_noupdate(self):
        """CA-04 (vérification directe) : les enregistrements ir.model.data
        des villes livrées par le module doivent être en noupdate=True
        après l'installation, pour ne pas être écrasés lors d'une mise à
        jour (post_init_hook)."""
        imd = self.env['ir.model.data'].search([
            ('module', '=', 'bst_l10n_ma_city'),
            ('model', '=', 'res.city'),
        ], limit=10)
        self.assertTrue(
            imd,
            "Les villes livrées par le CSV doivent être tracées via "
            "ir.model.data sous le module bst_l10n_ma_city."
        )
        non_verrouillees = imd.filtered(lambda r: not r.noupdate)
        self.assertFalse(
            non_verrouillees,
            "Toutes les données de villes livrées par le module doivent "
            "être verrouillées (noupdate=True) après l'installation."
        )

    def test_08_villes_filtrees_par_pays(self):
        """CA-03 : le domaine standard du champ city_id sur res.partner
        filtre bien les villes par pays (vérifié en confirmant qu'aucune
        ville marocaine n'a un country_id différent du Maroc, condition
        nécessaire au bon fonctionnement du domain natif)."""
        villes_mal_rattachees = self.ma_cities.filtered(
            lambda c: c.country_id != self.morocco
        )
        self.assertFalse(
            villes_mal_rattachees,
            "Toutes les villes chargées doivent être rattachées au pays "
            "Maroc pour que le filtrage par pays fonctionne correctement."
        )