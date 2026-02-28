from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAlertService(TransactionCase):
    """Test scheduled alert service for garment manufacturing."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Alert',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-ALR-001',
            'code': 'ST-ALR-001',
            'category': 'shirt',
        })
        cls.alert_model = cls.env['garment.alert.service']
        cls.employee = cls.env['hr.employee'].create({'name': 'Test Inspector Alert'})

    def test_alert_service_exists(self):
        """Alert service model should be registered."""
        self.assertIn('garment.alert.service', self.env.registry)

    # ------------------------------------------------------------------
    # Late Orders
    # ------------------------------------------------------------------
    def test_cron_late_orders_no_late(self):
        """Should not error when no late orders exist."""
        result = self.alert_model._cron_check_late_orders()
        self.assertTrue(result)

    def test_cron_late_orders_detects_late(self):
        """Should detect orders past delivery date."""
        past_date = fields.Date.today() - timedelta(days=5)
        self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'delivery_date': past_date,
        })
        # Should not raise an error
        result = self.alert_model._cron_check_late_orders()
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # QC Fail Rate
    # ------------------------------------------------------------------
    def test_cron_qc_fail_rate_no_issues(self):
        """Should not error when no QC issues exist."""
        result = self.alert_model._cron_check_qc_fail_rate()
        self.assertTrue(result)

    def test_cron_qc_fail_rate_detects_low_pass(self):
        """Should detect inspections with pass rate < 90%."""
        order = self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
        })
        self.env['garment.qc.inspection'].create({
            'inspection_type': 'inline',
            'garment_order_id': order.id,
            'inspector_id': self.employee.id,
            'inspection_date': fields.Datetime.now(),
            'inspected_qty': 100,
            'passed_qty': 70,
            'failed_qty': 30,
            'state': 'done',
        })
        result = self.alert_model._cron_check_qc_fail_rate()
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Upcoming Deliveries
    # ------------------------------------------------------------------
    def test_cron_upcoming_deliveries_no_upcoming(self):
        """Should not error when no upcoming deliveries exist."""
        result = self.alert_model._cron_check_upcoming_deliveries()
        self.assertTrue(result)

    def test_cron_upcoming_deliveries_detects_near(self):
        """Should detect orders with delivery in next 3 days."""
        near_date = fields.Date.today() + timedelta(days=2)
        self.env['garment.order'].create({
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'delivery_date': near_date,
        })
        result = self.alert_model._cron_check_upcoming_deliveries()
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Scheduled Actions (Cron Records)
    # ------------------------------------------------------------------
    def test_cron_records_exist(self):
        """All 3 cron records should exist."""
        cron_refs = [
            'garment_print.cron_check_late_orders',
            'garment_print.cron_check_qc_fail_rate',
            'garment_print.cron_check_upcoming_deliveries',
        ]
        for ref in cron_refs:
            cron = self.env.ref(ref)
            self.assertTrue(cron, f"Cron {ref} should exist")
            self.assertTrue(cron.active, f"Cron {ref} should be active")
            self.assertEqual(cron.interval_type, 'days')
