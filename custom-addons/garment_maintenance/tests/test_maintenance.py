from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestMaintenance(TransactionCase):
    """Unit tests and E2E tests for garment maintenance."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line MNT-Test',
            'code': 'LMNT01',
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Technician Test',
        })

    def _create_machine(self, **kwargs):
        vals = {
            'name': 'M-001',
            'machine_type': 'lockstitch',
            'brand': 'Juki',
            'serial_number': f'SN-{self.env["garment.machine"].search_count([])+1:05d}',
            'sewing_line_id': self.sewing_line.id,
            'maintenance_interval': 30,
        }
        vals.update(kwargs)
        return self.env['garment.machine'].create(vals)

    def _create_request(self, machine, **kwargs):
        vals = {
            'machine_id': machine.id,
            'request_type': 'corrective',
            'technician_id': self.employee.id,
        }
        vals.update(kwargs)
        return self.env['garment.maintenance.request'].create(vals)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_machine(self):
        machine = self._create_machine()
        self.assertEqual(machine.status, 'active')

    def test_serial_unique_constraint(self):
        """Serial numbers must be unique."""
        self._create_machine(serial_number='SN-UNIQUE-001')
        with self.assertRaises(Exception):
            self._create_machine(serial_number='SN-UNIQUE-001')

    def test_next_maintenance_date(self):
        from datetime import date, timedelta
        machine = self._create_machine(
            last_maintenance_date=date.today(),
            maintenance_interval=30,
        )
        expected = date.today() + timedelta(days=30)
        self.assertEqual(machine.next_maintenance_date, expected)

    def test_request_sequence(self):
        machine = self._create_machine()
        req = self._create_request(machine)
        self.assertTrue(req.name.startswith('MNT/'))

    def test_breakdown_sets_machine_broken(self):
        machine = self._create_machine()
        req = self._create_request(machine, request_type='breakdown')
        req.action_confirm()
        self.assertEqual(machine.status, 'broken')

    def test_done_sets_machine_active(self):
        machine = self._create_machine()
        req = self._create_request(machine, request_type='breakdown')
        req.action_confirm()
        req.action_start()
        req.action_done()
        self.assertEqual(machine.status, 'active')
        self.assertIsNotNone(machine.last_maintenance_date)

    def test_cannot_cancel_done_request(self):
        machine = self._create_machine()
        req = self._create_request(machine)
        req.action_confirm()
        req.action_start()
        req.action_done()
        with self.assertRaises(UserError):
            req.action_cancel()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_maintenance_workflow(self):
        """E2E: Machine → breakdown → request → fix → machine active again."""
        # Step 1: Create machine
        machine = self._create_machine(name='M-E2E-001')
        self.assertEqual(machine.status, 'active')

        # Step 2: Report breakdown
        req = self._create_request(
            machine,
            request_type='breakdown',
            description='Needle broken, thread jam',
        )
        self.assertEqual(req.state, 'draft')

        # Step 3: Confirm (machine goes broken)
        req.action_confirm()
        self.assertEqual(req.state, 'confirmed')
        self.assertEqual(machine.status, 'broken')

        # Step 4: Start repair
        req.action_start()
        self.assertEqual(req.state, 'in_progress')

        # Step 5: Complete repair
        req.write({
            'action_taken': 'Replaced needle and cleaned thread path',
            'spare_parts': 'Needle DB×1 #14',
            'cost': 50000,
            'downtime_hours': 1.5,
        })
        req.action_done()
        self.assertEqual(req.state, 'done')
        self.assertEqual(machine.status, 'active')
        self.assertIsNotNone(req.completion_date)

    def test_e2e_preventive_maintenance(self):
        """E2E: Scheduled preventive maintenance."""
        machine = self._create_machine(name='M-PM-001')
        req = self._create_request(
            machine,
            request_type='preventive',
            description='Monthly oil and clean',
        )
        req.action_confirm()
        self.assertEqual(machine.status, 'maintenance')

        req.action_start()
        req.action_done()
        self.assertEqual(machine.status, 'active')
