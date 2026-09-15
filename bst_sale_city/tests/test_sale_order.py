from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSaleOrderCity(TransactionCase):
    """Tests for Module 2 - bst_sale_city.
    Each test corresponds to an acceptance criterion from the specification."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.morocco = cls.env['res.country'].search([('code', '=', 'MA')], limit=1)
        cls.city_a, cls.city_b = cls.env['res.city'].search([
            ('country_id', '=', cls.morocco.id),
        ], limit=2)

        cls.partner_with_city = cls.env['res.partner'].create({
            'name': 'Customer With City',
            'country_id': cls.morocco.id,
            'city_id': cls.city_a.id,
        })
        cls.partner_other_city = cls.env['res.partner'].create({
            'name': 'Customer Other City',
            'country_id': cls.morocco.id,
            'city_id': cls.city_b.id,
        })
        cls.partner_without_city = cls.env['res.partner'].create({
            'name': 'Customer Without City',
            'country_id': cls.morocco.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'BF-CITIES-QUOTATION Test Product',
            'list_price': 100.0,
        })

    def _create_order(self, partner):
        """Simulates what the form would produce after the onchange."""
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'city_id': partner.city_id.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
            })],
        })

    def test_01_ville_reportee_a_la_creation(self):
        """CA-01: creating a quotation for a customer with a city
        fills in the field without user action (via onchange,
        manually triggered here to simulate the form)."""
        order = self.env['sale.order'].new({'partner_id': self.partner_with_city.id})
        order._onchange_partner_id_city()
        self.assertEqual(
            order.city_id, self.partner_with_city.city_id,
            "The quotation city must be automatically transferred from "
            "the customer when creating the quotation."
        )

    def test_02_changement_client_met_a_jour_ville(self):
        """CA-02: changing the customer on a quotation in draft updates
        the city."""
        order = self.env['sale.order'].new({'partner_id': self.partner_with_city.id})
        order._onchange_partner_id_city()
        self.assertEqual(order.city_id, self.city_a)

        order.partner_id = self.partner_other_city
        order._onchange_partner_id_city()
        self.assertEqual(
            order.city_id, self.city_b,
            "The city must be updated after changing the customer."
        )

    def test_03_modification_manuelle_ne_remonte_pas_sur_client(self):
        """CA-03: modifying the city on the quotation does not change
        the customer's record."""
        order = self._create_order(self.partner_with_city)
        order.city_id = self.city_b
        order.flush_recordset()

        self.assertEqual(
            order.city_id, self.city_b,
            "The quotation city must reflect the manual modification."
        )
        self.assertEqual(
            self.partner_with_city.city_id, self.city_a,
            "The customer's record must never be modified by a city "
            "change made from the quotation."
        )

    def test_04_confirmation_bloquee_sans_ville(self):
        """CA-04: confirming a quotation without a city raises an explicit
        error and the quotation remains in draft."""
        order = self._create_order(self.partner_without_city)
        self.assertFalse(order.city_id)

        with self.assertRaises(UserError):
            order.action_confirm()

        self.assertEqual(
            order.state, 'draft',
            "The quotation must remain in draft if confirmation "
            "fails because no city has been provided."
        )

    def test_05_devis_sans_ville_peut_etre_enregistre(self):
        """CA-05: a quotation without a city can be created and saved in
        draft without error (the restriction only applies to
        confirmation, not creation/saving)."""
        order = self._create_order(self.partner_without_city)
        self.assertTrue(order.id, "The quotation must be created without error.")
        self.assertEqual(order.state, 'draft')
        self.assertFalse(order.city_id)

    def test_06_confirmation_reussit_avec_ville(self):
        """CA-04 (nominal case): a quotation with a city provided is
        confirmed normally without error."""
        order = self._create_order(self.partner_with_city)
        self.assertTrue(order.city_id)
        order.action_confirm()
        self.assertEqual(
            order.state, 'sale',
            "The quotation must be confirmed normally when "
            "the city is provided."
        )

    def test_07_recherche_et_regroupement_par_ville(self):
        """CA-06: the city is available for search and grouping
        on the quotation list (here we verify that the field is
        searchable/groupable at the model level)."""
        order = self._create_order(self.partner_with_city)

        found = self.env['sale.order'].search([('city_id', '=', self.city_a.id)])
        self.assertIn(
            order, found,
            "The quotation must be findable by searching on city_id."
        )

        grouped = self.env['sale.order'].read_group(
            domain=[('id', '=', order.id)],
            fields=['city_id'],
            groupby=['city_id'],
        )
        self.assertTrue(
            grouped,
            "Grouping by city (city_id) must work without "
            "error on the sale.order model."
        )

    def test_08_commande_confirmee_avant_module_reste_consultable(self):
        """CA-08: an already confirmed order (even without a city, simulating
        an order created before the module was installed) remains
        accessible without error; the RG-06 constraint only applies to
        an explicit call to action_confirm(), never to simply reading
        an existing record."""
        order = self._create_order(self.partner_without_city)
        # Simulates an order confirmed before the module was deployed,
        # deliberately bypassing action_confirm() so as not to trigger
        # the RG-06 check (which did not exist at that time).
        order.write({'state': 'sale'})

        self.assertEqual(order.state, 'sale')
        self.assertFalse(order.city_id)
        # Simply reading the record must not raise any exception.
        self.assertTrue(order.name)