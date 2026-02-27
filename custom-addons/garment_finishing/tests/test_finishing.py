from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestFinishingOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Customer'})
        cls.style = cls.env['garment.style'].create({
            'name': 'Test Style FN',
            'code': 'TST-FN',
            'category': 'shirt',
        })
        cls.order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.order.id,
            'planned_qty': 1000,
        })
        cls.employee = cls.env['hr.employee'].create({'name': 'Worker FN'})

    def test_create_finishing_order(self):
        fo = self.env['garment.finishing.order'].create({
            'production_order_id': self.prod_order.id,
            'qty_received': 500,
        })
        self.assertTrue(fo.name.startswith('FN-'))
        self.assertEqual(fo.state, 'draft')
        self.assertEqual(fo.style_id, self.style)

    def test_full_workflow(self):
        fo = self.env['garment.finishing.order'].create({
            'production_order_id': self.prod_order.id,
            'qty_received': 100,
        })
        fo.action_confirm()
        self.assertEqual(fo.state, 'confirmed')
        fo.action_start()
        self.assertEqual(fo.state, 'in_progress')
        self.assertTrue(fo.date_start)
        fo.action_done()
        self.assertEqual(fo.state, 'done')
        self.assertTrue(fo.date_done)

    def test_task_summary_compute(self):
        fo = self.env['garment.finishing.order'].create({
            'production_order_id': self.prod_order.id,
            'qty_received': 200,
        })
        self.env['garment.finishing.task'].create([
            {
                'finishing_order_id': fo.id,
                'task_type': 'thread_cut',
                'qty_done': 180,
                'qty_defect': 5,
                'employee_id': self.employee.id,
            },
            {
                'finishing_order_id': fo.id,
                'task_type': 'pressing',
                'qty_done': 170,
                'qty_defect': 3,
            },
            {
                'finishing_order_id': fo.id,
                'task_type': 'tagging',
                'qty_done': 160,
            },
            {
                'finishing_order_id': fo.id,
                'task_type': 'folding',
                'qty_done': 150,
            },
            {
                'finishing_order_id': fo.id,
                'task_type': 'qc_check',
                'qty_done': 145,
                'qty_defect': 10,
            },
        ])
        self.assertEqual(fo.qty_thread_cut, 180)
        self.assertEqual(fo.qty_pressed, 170)
        self.assertEqual(fo.qty_tagged, 160)
        self.assertEqual(fo.qty_folded, 150)
        self.assertEqual(fo.qty_passed_qc, 145)
        self.assertEqual(fo.qty_defect, 18)

    def test_completion_rate(self):
        fo = self.env['garment.finishing.order'].create({
            'production_order_id': self.prod_order.id,
            'qty_received': 200,
        })
        self.env['garment.finishing.task'].create({
            'finishing_order_id': fo.id,
            'task_type': 'folding',
            'qty_done': 100,
        })
        self.assertAlmostEqual(fo.completion_rate, 50.0)

    def test_cannot_cancel_done(self):
        fo = self.env['garment.finishing.order'].create({
            'production_order_id': self.prod_order.id,
            'qty_received': 50,
        })
        fo.action_confirm()
        fo.action_start()
        fo.action_done()
        with self.assertRaises(UserError):
            fo.action_cancel()
