from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSaleOrderCity(TransactionCase):
    """Tests du Module 2 - bst_sale_city.
    Chaque test correspond à un critère d'acceptation du cahier des charges."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.morocco = cls.env['res.country'].search([('code', '=', 'MA')], limit=1)
        cls.city_a, cls.city_b = cls.env['res.city'].search([
            ('country_id', '=', cls.morocco.id),
        ], limit=2)

        cls.partner_with_city = cls.env['res.partner'].create({
            'name': 'Client Avec Ville',
            'country_id': cls.morocco.id,
            'city_id': cls.city_a.id,
        })
        cls.partner_other_city = cls.env['res.partner'].create({
            'name': 'Client Autre Ville',
            'country_id': cls.morocco.id,
            'city_id': cls.city_b.id,
        })
        cls.partner_without_city = cls.env['res.partner'].create({
            'name': 'Client Sans Ville',
            'country_id': cls.morocco.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit de test BF-VILLES-DEVIS',
            'list_price': 100.0,
        })

    def _create_order(self, partner):
        """Simule ce que produirait le formulaire une fois l'onchange"""
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'city_id': partner.city_id.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
            })],
        })

    def test_01_ville_reportee_a_la_creation(self):
        """CA-01 : la création d'un devis pour un client avec ville
        renseigne le champ sans action de l'utilisateur (via onchange,
        déclenché manuellement ici pour simuler le formulaire)."""
        order = self.env['sale.order'].new({'partner_id': self.partner_with_city.id})
        order._onchange_partner_id_city()
        self.assertEqual(
            order.city_id, self.partner_with_city.city_id,
            "La ville du devis doit être reportée automatiquement depuis "
            "le client à la création."
        )

    def test_02_changement_client_met_a_jour_ville(self):
        """CA-02 : un changement de client sur un devis en brouillon met la
        ville à jour."""
        order = self.env['sale.order'].new({'partner_id': self.partner_with_city.id})
        order._onchange_partner_id_city()
        self.assertEqual(order.city_id, self.city_a)

        order.partner_id = self.partner_other_city
        order._onchange_partner_id_city()
        self.assertEqual(
            order.city_id, self.city_b,
            "La ville doit être mise à jour après changement de client."
        )

    def test_03_modification_manuelle_ne_remonte_pas_sur_client(self):
        """CA-03 : la modification de la ville sur le devis ne change pas
        la fiche du client."""
        order = self._create_order(self.partner_with_city)
        order.city_id = self.city_b
        order.flush_recordset()

        self.assertEqual(
            order.city_id, self.city_b,
            "La ville du devis doit refléter la modification manuelle."
        )
        self.assertEqual(
            self.partner_with_city.city_id, self.city_a,
            "La fiche du client ne doit jamais être modifiée par un "
            "changement de ville fait depuis le devis."
        )

    def test_04_confirmation_bloquee_sans_ville(self):
        """CA-04 : la confirmation d'un devis sans ville lève une erreur
        explicite et le devis reste en brouillon."""
        order = self._create_order(self.partner_without_city)
        self.assertFalse(order.city_id)

        with self.assertRaises(UserError):
            order.action_confirm()

        self.assertEqual(
            order.state, 'draft',
            "Le devis doit rester en brouillon si la confirmation a "
            "échoué faute de ville renseignée."
        )

    def test_05_devis_sans_ville_peut_etre_enregistre(self):
        """CA-05 : un devis sans ville peut être créé et enregistré en
        brouillon sans erreur (le blocage ne s'applique qu'à la
        confirmation, pas à la création/sauvegarde)."""
        order = self._create_order(self.partner_without_city)
        self.assertTrue(order.id, "Le devis doit être créé sans erreur.")
        self.assertEqual(order.state, 'draft')
        self.assertFalse(order.city_id)

    def test_06_confirmation_reussit_avec_ville(self):
        """CA-04 (cas nominal) : un devis avec une ville renseignée se
        confirme normalement, sans erreur."""
        order = self._create_order(self.partner_with_city)
        self.assertTrue(order.city_id)
        order.action_confirm()
        self.assertEqual(
            order.state, 'sale',
            "Le devis doit pouvoir être confirmé normalement lorsque la "
            "ville est renseignée."
        )

    def test_07_recherche_et_regroupement_par_ville(self):
        """CA-06 : la ville est disponible en recherche et en regroupement
        sur la liste des devis (on vérifie ici que le champ est bien
        recherchable/groupable au niveau du modèle)."""
        order = self._create_order(self.partner_with_city)

        found = self.env['sale.order'].search([('city_id', '=', self.city_a.id)])
        self.assertIn(
            order, found,
            "Le devis doit être trouvable par une recherche sur city_id."
        )

        grouped = self.env['sale.order'].read_group(
            domain=[('id', '=', order.id)],
            fields=['city_id'],
            groupby=['city_id'],
        )
        self.assertTrue(
            grouped,
            "Le regroupement par ville (city_id) doit fonctionner sans "
            "erreur sur le modèle sale.order."
        )

    def test_08_commande_confirmee_avant_module_reste_consultable(self):
        """CA-08 : une commande déjà confirmée (même sans ville, simulant
        une commande antérieure à l'installation du module) reste
        consultable sans erreur ; la contrainte RG-06 ne s'applique qu'à
        l'appel explicite de action_confirm(), jamais à la simple lecture
        d'un enregistrement existant."""
        order = self._create_order(self.partner_without_city)
        # Simule une commande confirmée avant la mise en service du
        # module, en contournant volontairement action_confirm() pour ne
        # pas déclencher le contrôle RG-06 (qui n'existait pas à l'époque).
        order.write({'state': 'sale'})

        self.assertEqual(order.state, 'sale')
        self.assertFalse(order.city_id)
        # La simple lecture ne doit lever aucune exception.
        self.assertTrue(order.name)