from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAuditLog(TransactionCase):
    """Tests for garment.audit.log and garment.audit.mixin."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer Audit',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-AUD-001',
            'code': 'ST-AUD-001',
            'category': 'shirt',
        })

    def _create_order(self, **kwargs):
        vals = {
            'customer_id': self.partner.id,
            'style_id': self.style.id,
            'unit_price': 5.0,
        }
        vals.update(kwargs)
        return self.env['garment.order'].create(vals)

    # ----- CREATE -----
    def test_create_logs_audit(self):
        """Creating an order should generate an audit log entry."""
        order = self._create_order()
        logs = self.env['garment.audit.log'].search([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
            ('action', '=', 'create'),
        ])
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.severity, 'info')
        self.assertIn('Khách Hàng', logs.field_changes)

    # ----- WRITE -----
    def test_write_logs_changes(self):
        """Writing tracked fields should log changes with old→new values."""
        order = self._create_order()
        order.write({'unit_price': 10.0})
        logs = self.env['garment.audit.log'].search([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
            ('action', '=', 'write'),
        ])
        self.assertTrue(len(logs) >= 1)
        self.assertIn('→', logs[0].field_changes)

    def test_write_untracked_field_no_log(self):
        """Writing an untracked field should not generate audit log."""
        order = self._create_order()
        initial_count = self.env['garment.audit.log'].search_count([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
        ])
        # notes is not in _audit_tracked_fields
        order.write({'notes': 'test note'})
        count_after = self.env['garment.audit.log'].search_count([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
        ])
        # Only 'create' log should exist, no extra write log
        self.assertEqual(initial_count, count_after)

    # ----- STATE CHANGE -----
    def test_state_change_logged(self):
        """State changes should be logged as 'state_change' action."""
        order = self._create_order()
        order.write({'state': 'confirmed'})
        logs = self.env['garment.audit.log'].search([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
            ('action', '=', 'state_change'),
        ])
        self.assertTrue(len(logs) >= 1)
        self.assertTrue(logs[0].new_state)

    # ----- UNLINK -----
    def test_unlink_logs_critical(self):
        """Deleting a record should log with critical severity."""
        order = self._create_order()
        order_id = order.id
        order.unlink()
        logs = self.env['garment.audit.log'].search([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order_id),
            ('action', '=', 'unlink'),
        ])
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.severity, 'critical')

    # ----- SEVERITY -----
    def test_severity_cancelled(self):
        """Cancelling should produce warning severity."""
        order = self._create_order()
        order.write({'state': 'cancelled'})
        logs = self.env['garment.audit.log'].search([
            ('model_name', '=', 'garment.order'),
            ('res_id', '=', order.id),
            ('action', '=', 'state_change'),
        ])
        self.assertTrue(len(logs) >= 1)
        self.assertEqual(logs[0].severity, 'warning')

    # ----- LOG MODEL DIRECTLY -----
    def test_log_classmethod(self):
        """Direct call to GarmentAuditLog.log() should work."""
        log = self.env['garment.audit.log'].log(
            action='write',
            model_name='garment.order',
            res_id=999,
            record_name='Test Record',
            field_changes='Test Field: old → new',
            severity='info',
        )
        self.assertTrue(log.id)
        self.assertEqual(log.action, 'write')
        self.assertEqual(log.user_id.id, self.env.uid)

    # ----- FORMAT VALUE -----
    def test_format_selection_value(self):
        """Selection field values should show label, not key."""
        order = self._create_order()
        formatted = order._audit_format_value('state', 'draft')
        # Should return Vietnamese label, not 'draft'
        self.assertNotEqual(formatted, 'draft')
        self.assertTrue(len(formatted) > 0)

    def test_format_many2one_value(self):
        """Many2one field values should show display_name."""
        order = self._create_order()
        formatted = order._audit_format_value('customer_id', self.partner.id)
        self.assertIn('Test Buyer Audit', formatted)
