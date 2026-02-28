from datetime import datetime, timedelta
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDowntimeAnalysis(TransactionCase):
    """Tests for garment.downtime.analysis SQL view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'DT Test Line',
            'code': 'DTL1',
        })
        cls.machine = cls.env['garment.machine'].create({
            'name': 'MC-DT-001',
            'machine_type': 'lockstitch',
            'brand': 'Juki',
            'serial_number': 'SN-DT-001',
            'sewing_line_id': cls.sewing_line.id,
        })
        cls.technician = cls.env['hr.employee'].create({
            'name': 'Tech DT Test',
        })
        # Breakdown request with downtime
        now = datetime.now()
        cls.breakdown_req = cls.env['garment.maintenance.request'].create({
            'machine_id': cls.machine.id,
            'request_type': 'breakdown',
            'priority': '3',
            'technician_id': cls.technician.id,
            'description': 'Motor overheating',
            'downtime_hours': 4.5,
            'cost': 500000,
            'request_date': now - timedelta(hours=6),
            'completion_date': now,
        })
        # Preventive request
        cls.preventive_req = cls.env['garment.maintenance.request'].create({
            'machine_id': cls.machine.id,
            'request_type': 'preventive',
            'priority': '0',
            'technician_id': cls.technician.id,
            'downtime_hours': 1.0,
            'cost': 50000,
            'request_date': now - timedelta(hours=2),
            'completion_date': now - timedelta(hours=1),
        })

    def _refresh_view(self):
        self.env.flush_all()
        self.env['garment.downtime.analysis'].init()

    def test_sql_view_accessible(self):
        """Downtime analysis SQL view should be queryable."""
        records = self.env['garment.downtime.analysis'].search([])
        self.assertTrue(len(records) >= 2)

    def test_breakdown_fields(self):
        """Breakdown request should have correct fields."""
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', self.breakdown_req.id),
        ])
        self.assertEqual(len(analysis), 1)
        self.assertEqual(analysis.machine_id, self.machine)
        self.assertEqual(analysis.machine_type, 'lockstitch')
        self.assertEqual(analysis.request_type, 'breakdown')
        self.assertEqual(analysis.priority, '3')
        self.assertAlmostEqual(analysis.downtime_hours, 4.5, places=1)
        self.assertAlmostEqual(analysis.cost, 500000, places=0)
        self.assertEqual(analysis.is_breakdown, 1)

    def test_repair_hours_calculated(self):
        """Repair hours = completion_date - request_date in hours."""
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', self.breakdown_req.id),
        ])
        # 6 hours between request and completion
        self.assertAlmostEqual(analysis.repair_hours, 6.0, places=0)

    def test_preventive_not_breakdown(self):
        """Preventive request should have is_breakdown = 0."""
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', self.preventive_req.id),
        ])
        self.assertEqual(analysis.is_breakdown, 0)
        self.assertEqual(analysis.request_type, 'preventive')

    def test_sewing_line_linked(self):
        """Machine's sewing line should be available in analysis."""
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', self.breakdown_req.id),
        ])
        self.assertEqual(analysis.sewing_line_id, self.sewing_line)

    def test_technician_linked(self):
        """Technician should be linked through request."""
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', self.breakdown_req.id),
        ])
        self.assertEqual(analysis.technician_id, self.technician)

    def test_filter_by_machine(self):
        """Filter by machine should work on SQL view."""
        self._refresh_view()
        results = self.env['garment.downtime.analysis'].search([
            ('machine_id', '=', self.machine.id),
        ])
        self.assertEqual(len(results), 2)

    def test_filter_breakdown_only(self):
        """Filter for breakdowns only."""
        self._refresh_view()
        results = self.env['garment.downtime.analysis'].search([
            ('machine_id', '=', self.machine.id),
            ('request_type', '=', 'breakdown'),
        ])
        self.assertEqual(len(results), 1)
        self.assertEqual(results.request_id, self.breakdown_req)

    def test_no_completion_zero_repair(self):
        """Without completion_date, repair_hours should be 0."""
        req = self.env['garment.maintenance.request'].create({
            'machine_id': self.machine.id,
            'request_type': 'corrective',
            'downtime_hours': 2.0,
        })
        self._refresh_view()
        analysis = self.env['garment.downtime.analysis'].search([
            ('request_id', '=', req.id),
        ])
        self.assertAlmostEqual(analysis.repair_hours, 0, places=1)
