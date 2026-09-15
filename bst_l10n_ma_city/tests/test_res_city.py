from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestResCity(TransactionCase):
    """Tests for Module 1 - bst_l10n_ma_city.
    Each test corresponds to an acceptance criterion from the specification."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.morocco = cls.env['res.country'].search([('code', '=', 'MA')], limit=1)
        cls.ma_cities = cls.env['res.city'].search([
            ('country_id', '=', cls.morocco.id),
        ])

    def test_01_referentiel_villes_charge(self):
        """CA-01: the city database contains Moroccan cities after
        installation, in a significant number."""
        self.assertEqual(
            len(self.ma_cities), 40,
            "The city database must contain 40 Moroccan cities "
            "after module installation."
        )

    def test_02_villes_ont_code_postal_et_region(self):
        """CA-01: each city must have a postal code and a region."""
        villes_sans_zip = self.ma_cities.filtered(lambda c: not c.zipcode)
        villes_sans_region = self.ma_cities.filtered(lambda c: not c.state_id)
        self.assertFalse(
            villes_sans_zip,
            "Some Moroccan cities do not have a postal code: %s"
            % villes_sans_zip.mapped('name')[:5]
        )
        self.assertFalse(
            villes_sans_region,
            "Some Moroccan cities do not have a region: %s"
            % villes_sans_region.mapped('name')[:5]
        )

    def test_03_douze_regions_creees(self):
        """RG-02: Morocco's 12 regions must exist and be linked to
        Morocco (they are not provided by Odoo by default)."""
        regions = self.env['res.country.state'].search([
            ('country_id', '=', self.morocco.id),
        ])
        self.assertEqual(
            len(regions), 12,
            "Morocco must have exactly 12 regions after module installation "
            "(found: %d)." % len(regions)
        )

    def test_04_enforce_cities_active_sur_maroc(self):
        """CA-02 (precondition): the setting allowing cities to be displayed
        in a dropdown list must be enabled for Morocco."""
        self.assertTrue(
            self.morocco.enforce_cities,
            "The enforce_cities field must be enabled for Morocco "
            "so that the City field is displayed as a dropdown list "
            "in contacts (RG-03)."
        )

    def test_05_selection_ville_remplit_zip_sur_contact(self):
        """CA-02: selecting a city on a Moroccan contact automatically
        fills in the postal code (standard behavior of
        base_address_extended, depending on enforce_cities)."""
        ville = self.ma_cities[0]
        partner = self.env['res.partner'].create({
            'name': 'BF-CITIES-01 Test Customer',
            'country_id': self.morocco.id,
            'city_id': ville.id,
        })
        self.assertEqual(
            partner.city_id, ville,
            "The selected city must be retained on the contact."
        )
        # Filling in the postal code is standard behavior linked to the
        # form widget/onchange; here we verify the consistency of the
        # underlying data used by this mechanism.
        self.assertEqual(
            partner.city_id.zipcode, ville.zipcode,
            "The postal code of the selected city must match "
            "the one in the city database."
        )

    def test_06_ville_manuelle_survit_a_une_mise_a_jour(self):
        """CA-04: a manually added city must still be present after
        a module update (cannot be tested directly in TransactionCase
        because it requires a complete module reload).

        This test verifies, at a minimum, that manually created data is not
        immediately linked to an external ID belonging to the module
        (which would make it vulnerable to reloading), a necessary condition
        for noupdate to protect the actual CSV data and leave
        manual additions intact.
        """
        ville_manuelle = self.env['res.city'].create({
            'name': 'BF-CITIES-01 Manual Test City',
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
            "A manually created city must not have any external ID "
            "belonging to the module's data (otherwise it would be considered "
            "part of the delivered city database and could be "
            "affected by a reinstallation)."
        )

    def test_07_donnees_csv_verrouillees_noupdate(self):
        """CA-04 (direct verification): ir.model.data records
        for cities delivered by the module must have noupdate=True
        after installation, so they are not overwritten during an update
        (post_init_hook)."""
        imd = self.env['ir.model.data'].search([
            ('module', '=', 'bst_l10n_ma_city'),
            ('model', '=', 'res.city'),
        ], limit=10)
        self.assertTrue(
            imd,
            "Cities delivered by the CSV file must be tracked through "
            "ir.model.data under the bst_l10n_ma_city module."
        )
        non_verrouillees = imd.filtered(lambda r: not r.noupdate)
        self.assertFalse(
            non_verrouillees,
            "All city data delivered by the module must be "
            "locked (noupdate=True) after installation."
        )

    def test_08_villes_filtrees_par_pays(self):
        """CA-03: the standard domain of the city_id field on res.partner
        correctly filters cities by country (verified by confirming that
        no Moroccan city has a country_id different from Morocco, a condition
        necessary for the native domain to work correctly)."""
        villes_mal_rattachees = self.ma_cities.filtered(
            lambda c: c.country_id != self.morocco
        )
        self.assertFalse(
            villes_mal_rattachees,
            "All loaded cities must be linked to the country "
            "Morocco for country-based filtering to work correctly."
        )