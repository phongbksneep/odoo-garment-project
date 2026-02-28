from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProductionOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Test Style',
            'code': 'TS-PROD',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({
            'name': 'Red', 'code': 'RED-P',
        })
        cls.size = cls.env['garment.size'].create({
            'name': 'M', 'code': 'M-P', 'size_type': 'letter',
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': fields.Date.today() + timedelta(days=30),
            'unit_price': 5.0,
        })
        cls.env['garment.order.line'].create({
            'order_id': cls.order.id,
            'color_id': cls.color.id,
            'size_id': cls.size.id,
            'quantity': 500,
        })
        cls.order.action_confirm()
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line A',
            'code': 'LA-P',
            'line_type': 'sewing',
        })

    def _create_production_order(self, **kwargs):
        vals = {
            'garment_order_id': self.order.id,
            'sewing_line_id': self.sewing_line.id,
            'planned_qty': 200,
            'end_date': fields.Date.today() + timedelta(days=10),
        }
        vals.update(kwargs)
        return self.env['garment.production.order'].create(vals)

    # --- Sequence ---
    def test_name_auto_generated(self):
        po = self._create_production_order()
        self.assertNotEqual(po.name, 'New')

    # --- Constraints ---
    def test_planned_qty_positive(self):
        with self.assertRaises(ValidationError):
            self._create_production_order(planned_qty=0)

    def test_planned_qty_negative(self):
        with self.assertRaises(ValidationError):
            self._create_production_order(planned_qty=-10)

    def test_end_date_before_start(self):
        with self.assertRaises(ValidationError):
            self._create_production_order(
                start_date=fields.Date.today(),
                end_date=fields.Date.today() - timedelta(days=5),
            )

    # --- Workflow ---
    def test_workflow_full(self):
        po = self._create_production_order()
        self.assertEqual(po.state, 'draft')
        po.action_confirm()
        self.assertEqual(po.state, 'confirmed')
        po.action_start()
        self.assertEqual(po.state, 'in_progress')
        self.assertEqual(po.start_date, fields.Date.today())
        po.action_done()
        self.assertEqual(po.state, 'done')
        self.assertEqual(po.actual_end_date, fields.Date.today())

    def test_cancel_done_raises(self):
        po = self._create_production_order()
        po.action_confirm()
        po.action_start()
        po.action_done()
        with self.assertRaises(UserError):
            po.action_cancel()

    def test_cancel_and_reset(self):
        po = self._create_production_order()
        po.action_confirm()
        po.action_cancel()
        self.assertEqual(po.state, 'cancelled')
        po.action_reset_draft()
        self.assertEqual(po.state, 'draft')

    # --- Computed fields ---
    def test_completed_qty_from_daily(self):
        po = self._create_production_order()
        po.action_confirm()
        po.action_start()
        self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'output_qty': 50,
            'target_qty': 60,
            'shift': 'morning',
        })
        self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'output_qty': 30,
            'target_qty': 40,
            'shift': 'afternoon',
        })
        self.assertEqual(po.completed_qty, 80)

    def test_defect_qty_from_daily(self):
        po = self._create_production_order()
        self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'output_qty': 50,
            'defect_qty': 5,
            'shift': 'morning',
        })
        self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'output_qty': 40,
            'defect_qty': 3,
            'shift': 'afternoon',
        })
        self.assertEqual(po.defect_qty, 8)

    def test_completion_rate(self):
        po = self._create_production_order(planned_qty=100)
        self.env['garment.daily.output'].create({
            'production_order_id': po.id,
            'output_qty': 75,
            'shift': 'morning',
        })
        self.assertAlmostEqual(po.completion_rate, 75.0)

    def test_is_overdue_in_progress(self):
        po = self._create_production_order(
            start_date=fields.Date.today() - timedelta(days=10),
            end_date=fields.Date.today() - timedelta(days=3),
        )
        po.action_confirm()
        po.write({'state': 'in_progress'})
        self.assertTrue(po.is_overdue)
        self.assertEqual(po.delay_days, 3)

    def test_not_overdue_when_done(self):
        po = self._create_production_order(
            end_date=fields.Date.today() + timedelta(days=5),
        )
        po.action_confirm()
        po.action_start()
        po.action_done()
        self.assertFalse(po.is_overdue)
        self.assertEqual(po.delay_days, 0)

    def test_overdue_done_late(self):
        po = self._create_production_order(
            start_date=fields.Date.today() - timedelta(days=10),
            end_date=fields.Date.today() - timedelta(days=5),
        )
        po.action_confirm()
        po.write({'state': 'in_progress'})
        po.action_done()
        # actual_end_date = today, end_date = 5 days ago => 5 days late
        self.assertTrue(po.is_overdue)
        self.assertEqual(po.delay_days, 5)


@tagged('post_install', '-at_install')
class TestDailyOutput(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer DO',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'Style DO',
            'code': 'SD-PROD',
            'category': 'shirt',
        })
        cls.color = cls.env['garment.color'].create({
            'name': 'Blue', 'code': 'BLU-P',
        })
        cls.size = cls.env['garment.size'].create({
            'name': 'L', 'code': 'L-P', 'size_type': 'letter',
        })
        order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
            'delivery_date': fields.Date.today() + timedelta(days=30),
            'unit_price': 5.0,
        })
        cls.env['garment.order.line'].create({
            'order_id': order.id,
            'color_id': cls.color.id,
            'size_id': cls.size.id,
            'quantity': 500,
        })
        order.action_confirm()
        sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'Line B',
            'code': 'LB-P',
            'line_type': 'sewing',
        })
        cls.po = cls.env['garment.production.order'].create({
            'garment_order_id': order.id,
            'sewing_line_id': sewing_line.id,
            'planned_qty': 200,
        })

    def _create_output(self, **kwargs):
        vals = {
            'production_order_id': self.po.id,
            'output_qty': 100,
            'target_qty': 120,
            'shift': 'morning',
            'worker_count': 10,
            'working_hours': 8.0,
        }
        vals.update(kwargs)
        return self.env['garment.daily.output'].create(vals)

    # --- Constraints ---
    def test_negative_output_qty(self):
        with self.assertRaises(ValidationError):
            self._create_output(output_qty=-5)

    def test_negative_defect_qty(self):
        with self.assertRaises(ValidationError):
            self._create_output(defect_qty=-1)

    def test_negative_rework_qty(self):
        with self.assertRaises(ValidationError):
            self._create_output(rework_qty=-1)

    # --- Computed fields ---
    def test_efficiency(self):
        do = self._create_output(output_qty=80, target_qty=100)
        self.assertAlmostEqual(do.efficiency, 80.0)

    def test_efficiency_zero_target(self):
        do = self._create_output(output_qty=80, target_qty=0)
        self.assertAlmostEqual(do.efficiency, 0.0)

    def test_defect_rate(self):
        do = self._create_output(output_qty=90, defect_qty=10)
        self.assertAlmostEqual(do.defect_rate, 10.0)

    def test_pieces_per_hour(self):
        do = self._create_output(output_qty=80, worker_count=10, working_hours=8.0)
        # 80 / (10 * 8) = 1.0
        self.assertAlmostEqual(do.pieces_per_hour, 1.0)

    def test_pieces_per_hour_no_workers(self):
        do = self._create_output(output_qty=80, worker_count=0)
        self.assertAlmostEqual(do.pieces_per_hour, 0.0)
