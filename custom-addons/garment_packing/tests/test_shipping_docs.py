from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestShippingInstruction(TransactionCase):
    """Tests for garment.shipping.instruction."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer SI',
            'customer_rank': 1,
            'street': '123 Test St',
            'city': 'Ho Chi Minh City',
        })
        cls.packing_list = cls.env['garment.packing.list'].create({
            'buyer_id': cls.partner.id,
            'ship_mode': 'sea',
            'destination_port': 'Los Angeles',
            'vessel_name': 'Ever Given',
            'packing_type': 'ratio',
        })

    def _create_si(self, **kwargs):
        vals = {
            'packing_list_id': self.packing_list.id,
            'shipper_name': 'Garment Co. Ltd',
            'consignee_name': 'Test Buyer SI',
            'port_of_loading': 'Cat Lai, HCMC',
            'payment_term': 'lc',
            'incoterm': 'fob',
        }
        vals.update(kwargs)
        return self.env['garment.shipping.instruction'].create(vals)

    # --- Unit Tests ---
    def test_create_sequence(self):
        si = self._create_si()
        self.assertTrue(si.name.startswith('SI/'))

    def test_related_fields(self):
        si = self._create_si()
        self.assertEqual(si.buyer_id, self.partner)
        self.assertEqual(si.port_of_discharge, 'Los Angeles')
        self.assertEqual(si.vessel_name, 'Ever Given')
        self.assertEqual(si.ship_mode, 'sea')

    def test_default_documents(self):
        si = self._create_si()
        self.assertTrue(si.doc_commercial_invoice)
        self.assertTrue(si.doc_packing_list)
        self.assertTrue(si.doc_bill_of_lading)
        self.assertTrue(si.doc_certificate_of_origin)

    def test_cannot_cancel_done(self):
        si = self._create_si()
        si.action_confirm()
        si.action_send()
        si.action_done()
        with self.assertRaises(UserError):
            si.action_cancel()

    def test_smart_button_count(self):
        self._create_si()
        self._create_si()
        self.packing_list.invalidate_recordset()
        self.assertEqual(self.packing_list.si_count, 2)

    # --- E2E Test ---
    def test_e2e_si_workflow(self):
        """E2E: Create → Confirm → Send → Done."""
        si = self._create_si(
            cargo_description='100% Cotton T-Shirts',
            lc_number='LC-2024-001',
        )
        self.assertEqual(si.state, 'draft')

        si.action_confirm()
        self.assertEqual(si.state, 'confirmed')

        si.action_send()
        self.assertEqual(si.state, 'sent')

        si.action_done()
        self.assertEqual(si.state, 'done')

    def test_reset_cancelled(self):
        si = self._create_si()
        si.action_cancel()
        self.assertEqual(si.state, 'cancelled')
        si.action_reset()
        self.assertEqual(si.state, 'draft')


@tagged('post_install', '-at_install')
class TestCertificateOrigin(TransactionCase):
    """Tests for garment.certificate.origin."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer CO',
            'customer_rank': 1,
            'street': '456 Buyer Ave',
            'city': 'Seoul',
        })
        cls.packing_list = cls.env['garment.packing.list'].create({
            'buyer_id': cls.partner.id,
            'ship_mode': 'sea',
            'destination_port': 'Busan',
            'packing_type': 'solid',
        })

    def _create_co(self, **kwargs):
        vals = {
            'packing_list_id': self.packing_list.id,
            'co_type': 'form_ak',
            'country_of_origin': 'Vietnam',
            'destination_country': 'Korea',
            'exporter_name': 'Garment Co. Ltd',
            'importer_name': 'Test Buyer CO',
        }
        vals.update(kwargs)
        return self.env['garment.certificate.origin'].create(vals)

    # --- Unit Tests ---
    def test_create_sequence(self):
        co = self._create_co()
        self.assertTrue(co.name.startswith('CO/'))

    def test_related_fields(self):
        co = self._create_co()
        self.assertEqual(co.buyer_id, self.partner)
        self.assertEqual(co.port_of_discharge, 'Busan')

    def test_co_line_creation(self):
        co = self._create_co()
        self.env['garment.certificate.origin.line'].create({
            'certificate_id': co.id,
            'description': '100% Cotton T-Shirts',
            'hs_code': '6109.10',
            'quantity': 5000,
            'weight': 2500,
            'fob_value': 15000,
            'origin_criteria': 'ctc',
        })
        self.assertEqual(len(co.line_ids), 1)
        self.assertEqual(co.line_ids[0].hs_code, '6109.10')

    def test_cannot_cancel_issued(self):
        co = self._create_co()
        co.action_apply()
        co.action_approve()
        co.action_issue()
        with self.assertRaises(UserError):
            co.action_cancel()

    def test_smart_button_count(self):
        self._create_co()
        self.packing_list.invalidate_recordset()
        self.assertEqual(self.packing_list.co_count, 1)

    # --- E2E Test ---
    def test_e2e_co_workflow(self):
        """E2E: Create → Apply → Approve → Issue."""
        co = self._create_co(
            invoice_number='INV-2024-100',
            invoice_date='2024-12-01',
        )
        self.assertEqual(co.state, 'draft')

        # Add line items
        self.env['garment.certificate.origin.line'].create([
            {
                'certificate_id': co.id,
                'description': '100% Cotton T-Shirts',
                'hs_code': '6109.10',
                'quantity': 5000,
                'weight': 2500,
                'fob_value': 15000,
                'origin_criteria': 'ctc',
            },
            {
                'certificate_id': co.id,
                'description': 'Polyester Jackets',
                'hs_code': '6201.93',
                'quantity': 2000,
                'weight': 3000,
                'fob_value': 20000,
                'origin_criteria': 'rvc',
            },
        ])
        self.assertEqual(len(co.line_ids), 2)

        co.action_apply()
        self.assertEqual(co.state, 'applied')

        co.action_approve()
        self.assertEqual(co.state, 'approved')

        co.action_issue()
        self.assertEqual(co.state, 'issued')

    def test_reset_cancelled(self):
        co = self._create_co()
        co.action_cancel()
        self.assertEqual(co.state, 'cancelled')
        co.action_reset()
        self.assertEqual(co.state, 'draft')
