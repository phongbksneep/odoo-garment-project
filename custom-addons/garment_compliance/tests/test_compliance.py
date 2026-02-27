from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from datetime import date, timedelta


@tagged('post_install', '-at_install')
class TestCompliance(TransactionCase):
    """Unit tests and E2E tests for garment compliance."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Compliance',
            'customer_rank': 1,
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Compliance Officer',
        })

    def _create_audit(self, **kwargs):
        vals = {
            'audit_type': 'bsci',
            'audit_date': date.today(),
            'auditor': 'TÜV SÜD',
            'buyer_id': self.partner.id,
        }
        vals.update(kwargs)
        return self.env['garment.compliance.audit'].create(vals)

    def _add_findings(self, audit, critical=0, major=0, minor=0):
        """Helper to add findings of different severities."""
        findings = []
        for i in range(critical):
            findings.append({
                'audit_id': audit.id,
                'category': 'health_safety',
                'severity': 'critical',
                'description': f'Critical finding #{i+1}',
            })
        for i in range(major):
            findings.append({
                'audit_id': audit.id,
                'category': 'labor',
                'severity': 'major',
                'description': f'Major finding #{i+1}',
            })
        for i in range(minor):
            findings.append({
                'audit_id': audit.id,
                'category': 'management',
                'severity': 'minor',
                'description': f'Minor finding #{i+1}',
            })
        return self.env['garment.audit.finding'].create(findings)

    # -------------------------------------------------------------------------
    # Unit Tests
    # -------------------------------------------------------------------------
    def test_create_audit_sequence(self):
        audit = self._create_audit()
        self.assertTrue(audit.name.startswith('AUD/'))

    def test_default_state_scheduled(self):
        audit = self._create_audit()
        self.assertEqual(audit.state, 'scheduled')

    def test_findings_count(self):
        audit = self._create_audit()
        self._add_findings(audit, critical=2, major=3, minor=1)
        audit.invalidate_recordset()
        self.assertEqual(audit.total_findings, 6)
        self.assertEqual(audit.critical_findings, 2)

    def test_complete_with_critical_goes_cap_required(self):
        """Completing an audit with critical findings → cap_required state."""
        audit = self._create_audit()
        self._add_findings(audit, critical=1)
        audit.action_start()
        audit.action_complete()
        self.assertEqual(audit.state, 'cap_required')

    def test_complete_without_critical_goes_completed(self):
        """Completing with no critical findings → completed state."""
        audit = self._create_audit()
        self._add_findings(audit, minor=2)
        audit.action_start()
        audit.action_complete()
        self.assertEqual(audit.state, 'completed')

    def test_cap_sequence(self):
        cap = self.env['garment.corrective.action'].create({
            'audit_id': self._create_audit().id,
            'description': 'Test CAP',
        })
        self.assertTrue(cap.name.startswith('CAP/'))

    def test_cap_overdue(self):
        audit = self._create_audit()
        cap = self.env['garment.corrective.action'].create({
            'audit_id': audit.id,
            'description': 'Overdue CAP',
            'deadline': date.today() - timedelta(days=1),
        })
        self.assertTrue(cap.is_overdue)

    def test_cap_not_overdue_when_done(self):
        audit = self._create_audit()
        cap = self.env['garment.corrective.action'].create({
            'audit_id': audit.id,
            'description': 'Done CAP',
            'deadline': date.today() - timedelta(days=1),
            'state': 'done',
        })
        self.assertFalse(cap.is_overdue)

    def test_cannot_submit_cap_without_action(self):
        audit = self._create_audit()
        cap = self.env['garment.corrective.action'].create({
            'audit_id': audit.id,
            'description': 'Need action',
        })
        cap.action_start()
        with self.assertRaises(UserError):
            cap.action_submit()

    def test_cannot_close_audit_with_open_caps(self):
        audit = self._create_audit()
        self._add_findings(audit, critical=1)
        audit.action_start()
        audit.action_complete()
        audit.action_create_cap()
        with self.assertRaises(UserError):
            audit.action_close()

    # -------------------------------------------------------------------------
    # E2E Test
    # -------------------------------------------------------------------------
    def test_e2e_full_compliance_workflow(self):
        """E2E: Audit → findings → CAP → fix → verify → close audit."""
        # Step 1: Schedule audit
        audit = self._create_audit(
            audit_type='bsci',
            auditor='SGS',
            expiry_date=date.today() + timedelta(days=365),
        )
        self.assertEqual(audit.state, 'scheduled')

        # Step 2: Start audit
        audit.action_start()
        self.assertEqual(audit.state, 'in_progress')

        # Step 3: Record findings
        self._add_findings(audit, critical=1, major=2, minor=3)
        audit.invalidate_recordset()
        self.assertEqual(audit.total_findings, 6)

        # Step 4: Complete audit (goes to cap_required due to critical)
        audit.action_complete()
        self.assertEqual(audit.state, 'cap_required')
        audit.write({'overall_rating': 'd'})

        # Step 5: Create CAPs automatically
        audit.action_create_cap()
        # Should create CAPs for critical + major = 3
        self.assertEqual(len(audit.cap_ids), 3)

        # Step 6: Process all CAPs
        for cap in audit.cap_ids:
            cap.write({
                'responsible_id': self.employee.id,
                'deadline': date.today() + timedelta(days=30),
                'root_cause': 'Inadequate training',
                'corrective_action': 'Retrain all workers',
                'preventive_action': 'Monthly refresher training',
            })
            cap.action_start()
            cap.action_submit()
            cap.action_verify()
            self.assertEqual(cap.state, 'done')

        # Step 7: Close audit
        audit.action_close()
        self.assertEqual(audit.state, 'closed')

    def test_e2e_clean_audit(self):
        """E2E: Clean audit with no critical findings → direct close."""
        audit = self._create_audit(audit_type='wrap')
        audit.action_start()
        self._add_findings(audit, minor=1)
        audit.action_complete()
        self.assertEqual(audit.state, 'completed')
        audit.write({'overall_rating': 'b'})
        audit.action_close()
        self.assertEqual(audit.state, 'closed')
