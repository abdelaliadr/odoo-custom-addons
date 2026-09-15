from datetime import datetime

from odoo.tests.common import TransactionCase


class TestServiceIntervention(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Intervention = cls.env["service.intervention"]
        cls.Partner = cls.env["res.partner"]
        cls.Technician = cls.env["service.technician"]

        # Test client
        cls.partner = cls.Partner.create({
            "name": "Test Client",
        })

        # Test technician
        cls.technician = cls.Technician.create({
            "name": "Test Technician",
        })

        # Test intervention in draft
        cls.draft = cls.Intervention.create({
            "partner_id": cls.partner.id,
            "name": "Test Draft",
            "state": "draft",
        })

        # Test intervention planned
        cls.planned = cls.Intervention.create({
            "partner_id": cls.partner.id,
            "name": "Test Planned",
            "state": "planned",
            "technician_id": cls.technician.id,
        })

        # Test intervention in progress
        cls.in_progress = cls.Intervention.create({
            "partner_id": cls.partner.id,
            "name": "Test In Progress",
            "state": "in_progress",
            "technician_id": cls.technician.id,
        })

        # Test intervention done
        cls.done = cls.Intervention.create({
            "partner_id": cls.partner.id,
            "name": "Test Done",
            "state": "done",
            "technician_id": cls.technician.id,
        })

    def test_intervention_searches(self):

        # 1. Recherche des interventions en brouillon
        draft = self.Intervention.search([
            ("state", "=", "draft"),
        ])

        self.assertTrue(draft)
        self.assertIn(self.draft, draft)

        for intervention in draft:
            self.assertEqual(intervention.state, "draft")

        # 2. Recherche d'un client
        partner = self.Partner.search([
            ("name", "=", "Test Client"),
        ], limit=1)

        self.assertTrue(partner)
        self.assertEqual(partner, self.partner)

        # 3. Interventions planifiées pour ce client
        planned_for_partner = self.Intervention.search([
            ("state", "=", "planned"),
            ("partner_id", "=", partner.id),
        ])

        self.assertTrue(planned_for_partner)
        self.assertIn(self.planned, planned_for_partner)

        for intervention in planned_for_partner:
            self.assertEqual(intervention.state, "planned")
            self.assertEqual(intervention.partner_id, partner)

        # 4. Interventions en cours ou terminées
        active_or_done = self.Intervention.search([
            "|",
            ("state", "=", "in_progress"),
            ("state", "=", "done"),
        ])

        self.assertTrue(active_or_done)
        self.assertIn(self.in_progress, active_or_done)
        self.assertIn(self.done, active_or_done)

        for intervention in active_or_done:
            self.assertIn(
                intervention.state,
                ["in_progress", "done"],
            )

        # 5. Recherche de toutes les interventions
        all_interventions = self.Intervention.search([])

        self.assertTrue(all_interventions)

        self.assertIn(self.draft, all_interventions)
        self.assertIn(self.planned, all_interventions)
        self.assertIn(self.in_progress, all_interventions)
        self.assertIn(self.done, all_interventions)

        # 6. browse() + exists()
        one_record = self.Intervention.browse(self.draft.id)

        self.assertTrue(one_record.exists())
        self.assertTrue(one_record.name)

        # 7. mapped()
        client_names = self.Intervention.search([]).mapped(
            "partner_id.name"
        )

        self.assertIn("Test Client", client_names)

        for name in client_names:
            self.assertTrue(name)

        # 8. filtered()
        unassigned = self.Intervention.search([]).filtered(
            lambda intervention: not intervention.technician_id
        )

        self.assertIn(self.draft, unassigned)

        for intervention in unassigned:
            self.assertFalse(intervention.technician_id)

        # 9. sorted()
        by_date = self.Intervention.search([]).sorted(
            key=lambda intervention: (
                intervention.date_planned or datetime.min
            ),
            reverse=True,
        )

        dates = [
            intervention.date_planned
            for intervention in by_date
            if intervention.date_planned
        ]

        self.assertEqual(
            dates,
            sorted(dates, reverse=True),
        )

        # 10. _read_group() : interventions par technicien
        result = self.Intervention._read_group(
            domain=[],
            groupby=["technician_id"],
            aggregates=["__count"],
        )

        self.assertIsNotNone(result)

        for technician, count in result:
            self.assertGreaterEqual(count, 1)

        # 11. Clients avec plus de 3 interventions non facturées
        result = self.Intervention._read_group(
            domain=[
                ("state", "!=", "invoiced"),
            ],
            groupby=["partner_id"],
            aggregates=["__count"],
        )

        heavy_clients = [
            partner
            for partner, count in result
            if partner and count > 3
        ]

        self.assertIn(self.partner, heavy_clients)

        for partner in heavy_clients:
            self.assertTrue(partner)
