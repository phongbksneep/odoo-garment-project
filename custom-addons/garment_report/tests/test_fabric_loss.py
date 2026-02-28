from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFabricLossAnalysis(TransactionCase):
    """Tests for garment.fabric.loss.analysis SQL view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Buyer FabricLoss',
            'customer_rank': 1,
        })
        cls.style = cls.env['garment.style'].create({
            'name': 'STYLE-FL-001',
            'code': 'ST-FL-001',
            'category': 'shirt',
        })
        cls.fabric = cls.env['garment.fabric'].create({
            'name': 'Twill Cotton FL',
            'code': 'FAB-FL-001',
            'fabric_type': 'woven',
            'composition': '100% Cotton',
        })
        cls.garment_order = cls.env['garment.order'].create({
            'customer_id': cls.partner.id,
            'style_id': cls.style.id,
        })
        cls.sewing_line = cls.env['garment.sewing.line'].create({
            'name': 'FL Test Line',
            'code': 'FL01',
        })
        cls.prod_order = cls.env['garment.production.order'].create({
            'garment_order_id': cls.garment_order.id,
            'sewing_line_id': cls.sewing_line.id,
            'planned_qty': 1000,
        })
        # Cutting order with marker info
        cls.cutting_order = cls.env['garment.cutting.order.adv'].create({
            'production_order_id': cls.prod_order.id,
            'fabric_id': cls.fabric.id,
            'marker_length': 10.0,
            'marker_width': 150.0,
            'marker_efficiency': 85.0,
        })

    def _add_layers(self, cutting_order, lengths):
        """Add spreading layers with given lengths."""
        for i, length in enumerate(lengths):
            self.env['garment.cutting.layer'].create({
                'cutting_order_id': cutting_order.id,
                'fabric_roll_no': 'ROLL-%03d' % (i + 1),
                'length': length,
            })

    def _add_bundles(self, cutting_order, quantities):
        """Add bundles with given piece quantities."""
        size = self.env['garment.size'].search([], limit=1)
        if not size:
            size = self.env['garment.size'].create({
                'name': 'M-FL', 'code': 'MFL', 'size_type': 'letter',
            })
        for i, qty in enumerate(quantities):
            self.env['garment.cutting.bundle'].create({
                'cutting_order_id': cutting_order.id,
                'bundle_no': 'BDL-%03d' % (i + 1),
                'size_id': size.id,
                'quantity': qty,
            })

    def _refresh_view(self):
        """Flush data and re-init SQL view."""
        self.env.flush_all()
        self.env['garment.fabric.loss.analysis'].init()

    def test_sql_view_accessible(self):
        """Fabric loss SQL view should be queryable."""
        records = self.env['garment.fabric.loss.analysis'].search([])
        self.assertTrue(len(records) >= 1)

    def test_dimensions_correct(self):
        """Dimension fields should link correctly."""
        self._refresh_view()
        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        self.assertEqual(len(analysis), 1)
        self.assertEqual(analysis.style_id, self.style)
        self.assertEqual(analysis.fabric_id, self.fabric)
        self.assertEqual(analysis.production_order_id, self.prod_order)

    def test_no_layers_zero_planned(self):
        """Without layers, planned fabric should be 0."""
        self._refresh_view()
        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        self.assertEqual(analysis.planned_fabric, 0)
        self.assertEqual(analysis.actual_fabric, 0)

    def test_planned_vs_actual_fabric(self):
        """With layers, planned = marker_length × layers, actual = sum(lengths)."""
        # marker_length = 10.0m, add 5 layers each 10.5m (slightly longer)
        self._add_layers(self.cutting_order, [10.5, 10.5, 10.5, 10.5, 10.5])
        self._refresh_view()

        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        # planned = 10.0 * 5 = 50.0
        self.assertAlmostEqual(analysis.planned_fabric, 50.0, places=1)
        # actual = 10.5 * 5 = 52.5
        self.assertAlmostEqual(analysis.actual_fabric, 52.5, places=1)
        # variance = 52.5 - 50.0 = 2.5
        self.assertAlmostEqual(analysis.fabric_variance, 2.5, places=1)
        # loss_pct = 2.5 / 50.0 * 100 = 5.0%
        self.assertAlmostEqual(analysis.loss_pct, 5.0, places=1)

    def test_good_cut_rate(self):
        """Good cut rate = (pieces - defective) / pieces × 100."""
        self._add_layers(self.cutting_order, [10.0, 10.0, 10.0])
        self._add_bundles(self.cutting_order, [50, 50, 50, 50])  # 200 pieces
        self.cutting_order.write({'defective_pieces': 10})
        self._refresh_view()

        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        self.assertEqual(analysis.total_pieces_cut, 200)
        self.assertEqual(analysis.defective_pieces, 10)
        # good_cut_rate = (200 - 10) / 200 * 100 = 95.0%
        self.assertAlmostEqual(analysis.good_cut_rate, 95.0, places=1)

    def test_fabric_per_piece(self):
        """Fabric per piece = actual_fabric / total_pieces_cut."""
        self._add_layers(self.cutting_order, [10.0, 10.0])
        self._add_bundles(self.cutting_order, [40, 40, 20])  # 100 pieces
        self._refresh_view()

        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        # actual = 20.0m, pieces = 100 → 0.2 m/piece
        self.assertAlmostEqual(analysis.fabric_per_piece, 0.2, places=3)

    def test_layer_quality_aggregation(self):
        """Layer defects and splices should be aggregated."""
        for i in range(3):
            self.env['garment.cutting.layer'].create({
                'cutting_order_id': self.cutting_order.id,
                'fabric_roll_no': 'ROLL-Q%d' % i,
                'length': 10.0,
                'defects_found': 2,
                'splice_count': 1,
            })
        self._refresh_view()

        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        self.assertEqual(analysis.total_defects, 6)
        self.assertEqual(analysis.total_splices, 3)

    def test_wastage_kg(self):
        """Wastage in kg should be reported."""
        self.cutting_order.write({'wastage_kg': 3.5})
        self._refresh_view()

        analysis = self.env['garment.fabric.loss.analysis'].search([
            ('cutting_order_id', '=', self.cutting_order.id),
        ])
        self.assertAlmostEqual(analysis.wastage_kg, 3.5, places=1)

    def test_search_filters(self):
        """Search filters should work on SQL view fields."""
        self._refresh_view()
        results = self.env['garment.fabric.loss.analysis'].search([
            ('style_id', '=', self.style.id),
        ])
        self.assertTrue(len(results) >= 1)

        results = self.env['garment.fabric.loss.analysis'].search([
            ('fabric_id', '=', self.fabric.id),
        ])
        self.assertTrue(len(results) >= 1)
