from odoo import models, fields, api, tools


class GarmentDashboard(models.Model):
    """Dashboard tổng quan nhà máy may - SQL View tổng hợp KPI."""
    _name = 'garment.dashboard'
    _description = 'Dashboard Tổng Quan'
    _auto = False
    _order = 'id'

    name = fields.Char(string='Tên', readonly=True)
    kpi_type = fields.Selection([
        ('order_total', 'Tổng Đơn Hàng'),
        ('order_active', 'Đơn Đang SX'),
        ('order_done', 'Đơn Hoàn Thành'),
        ('order_late', 'Đơn Trễ Hạn'),
        ('prod_total', 'Tổng LSX'),
        ('prod_active', 'LSX Đang Chạy'),
        ('prod_done', 'LSX Hoàn Thành'),
        ('qty_planned', 'SL Kế Hoạch'),
        ('qty_completed', 'SL Hoàn Thành'),
        ('qty_defect', 'SL Lỗi'),
        ('qc_total', 'Tổng QC'),
        ('qc_pass', 'QC Đạt'),
        ('qc_fail', 'QC Không Đạt'),
        ('delivery_total', 'Tổng Giao Hàng'),
        ('delivery_done', 'Đã Giao'),
        ('material_total', 'Tổng Phiếu Nhập NL'),
        ('material_done', 'Phiếu NL Hoàn Thành'),
    ], string='Loại KPI', readonly=True)
    value = fields.Float(string='Giá Trị', readonly=True)
    percentage = fields.Float(string='Phần Trăm (%)', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                -- Tổng đơn hàng
                SELECT 1 AS id, 'Tổng Đơn Hàng' AS name, 'order_total' AS kpi_type,
                    COUNT(*)::float AS value, 0 AS percentage
                FROM garment_order WHERE state != 'cancelled'
                UNION ALL
                -- Đơn đang SX (material -> packing)
                SELECT 2, 'Đơn Đang SX', 'order_active',
                    COUNT(*)::float, 0
                FROM garment_order WHERE state IN ('material','cutting','sewing','finishing','qc','packing')
                UNION ALL
                -- Đơn hoàn thành
                SELECT 3, 'Đơn Hoàn Thành', 'order_done',
                    COUNT(*)::float, 0
                FROM garment_order WHERE state IN ('shipped','done')
                UNION ALL
                -- Đơn trễ hạn
                SELECT 4, 'Đơn Trễ Hạn', 'order_late',
                    COUNT(*)::float, 0
                FROM garment_order
                WHERE delivery_date < CURRENT_DATE
                    AND state NOT IN ('shipped','done','cancelled')
                UNION ALL
                -- Tổng LSX
                SELECT 5, 'Tổng LSX', 'prod_total',
                    COUNT(*)::float, 0
                FROM garment_production_order WHERE state != 'cancelled'
                UNION ALL
                -- LSX đang chạy
                SELECT 6, 'LSX Đang Chạy', 'prod_active',
                    COUNT(*)::float, 0
                FROM garment_production_order WHERE state = 'in_progress'
                UNION ALL
                -- LSX hoàn thành
                SELECT 7, 'LSX Hoàn Thành', 'prod_done',
                    COUNT(*)::float, 0
                FROM garment_production_order WHERE state = 'done'
                UNION ALL
                -- SL kế hoạch
                SELECT 8, 'SL Kế Hoạch', 'qty_planned',
                    COALESCE(SUM(planned_qty), 0)::float, 0
                FROM garment_production_order WHERE state != 'cancelled'
                UNION ALL
                -- SL hoàn thành
                SELECT 9, 'SL Hoàn Thành', 'qty_completed',
                    COALESCE(SUM(completed_qty), 0)::float, 0
                FROM garment_production_order WHERE state != 'cancelled'
                UNION ALL
                -- SL lỗi
                SELECT 10, 'SL Lỗi', 'qty_defect',
                    COALESCE(SUM(defect_qty), 0)::float, 0
                FROM garment_production_order WHERE state != 'cancelled'
                UNION ALL
                -- Tổng QC
                SELECT 11, 'Tổng QC', 'qc_total',
                    COUNT(*)::float, 0
                FROM garment_qc_inspection WHERE state != 'cancelled'
                UNION ALL
                -- QC đạt
                SELECT 12, 'QC Đạt', 'qc_pass',
                    COUNT(*)::float, 0
                FROM garment_qc_inspection WHERE result = 'pass' AND state != 'cancelled'
                UNION ALL
                -- QC không đạt
                SELECT 13, 'QC Không Đạt', 'qc_fail',
                    COUNT(*)::float, 0
                FROM garment_qc_inspection WHERE result = 'fail' AND state != 'cancelled'
                UNION ALL
                -- Tổng giao hàng
                SELECT 14, 'Tổng Giao Hàng', 'delivery_total',
                    COUNT(*)::float, 0
                FROM garment_delivery_order WHERE state != 'cancelled'
                UNION ALL
                -- Đã giao
                SELECT 15, 'Đã Giao', 'delivery_done',
                    COUNT(*)::float, 0
                FROM garment_delivery_order WHERE state = 'delivered'
                UNION ALL
                -- Tổng phiếu nhập NL
                SELECT 16, 'Tổng Phiếu Nhập NL', 'material_total',
                    COUNT(*)::float, 0
                FROM garment_material_receipt WHERE state != 'cancelled'
                UNION ALL
                -- Phiếu NL hoàn thành
                SELECT 17, 'Phiếu NL Hoàn Thành', 'material_done',
                    COUNT(*)::float, 0
                FROM garment_material_receipt WHERE state = 'done'
            )
        """ % self._table)


class GarmentOrderOverview(models.Model):
    """SQL View - Tổng quan đơn hàng theo trạng thái."""
    _name = 'garment.order.overview'
    _description = 'Tổng Quan Đơn Hàng'
    _auto = False
    _order = 'delivery_date'

    name = fields.Char(string='Số Đơn Hàng', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Khách Hàng', readonly=True)
    style_id = fields.Many2one('garment.style', string='Mẫu May', readonly=True)
    order_date = fields.Date(string='Ngày Đặt', readonly=True)
    delivery_date = fields.Date(string='Ngày Giao', readonly=True)
    total_qty = fields.Integer(string='Tổng SL', readonly=True)
    total_amount = fields.Float(string='Tổng Tiền', readonly=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('material', 'Chuẩn Bị NL'),
        ('cutting', 'Đang Cắt'),
        ('sewing', 'Đang May'),
        ('finishing', 'Hoàn Thiện'),
        ('qc', 'QC'),
        ('packing', 'Đóng Gói'),
        ('shipped', 'Đã Giao'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', readonly=True)
    days_remaining = fields.Integer(string='Ngày Còn Lại', readonly=True)
    is_late = fields.Boolean(string='Trễ Hạn', readonly=True)
    production_count = fields.Integer(string='Số LSX', readonly=True)
    completion_rate = fields.Float(string='% Hoàn Thành', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    o.id,
                    o.name,
                    o.customer_id,
                    o.style_id,
                    o.order_date,
                    o.delivery_date,
                    o.total_qty,
                    o.total_amount,
                    o.state,
                    CASE
                        WHEN o.delivery_date IS NOT NULL
                        THEN (o.delivery_date - CURRENT_DATE)
                        ELSE 0
                    END AS days_remaining,
                    CASE
                        WHEN o.delivery_date IS NOT NULL
                            AND o.delivery_date < CURRENT_DATE
                            AND o.state NOT IN ('shipped','done','cancelled')
                        THEN TRUE
                        ELSE FALSE
                    END AS is_late,
                    COALESCE(p.prod_count, 0) AS production_count,
                    COALESCE(p.avg_completion, 0) AS completion_rate
                FROM garment_order o
                LEFT JOIN (
                    SELECT
                        garment_order_id,
                        COUNT(*) AS prod_count,
                        AVG(completion_rate) AS avg_completion
                    FROM garment_production_order
                    WHERE state != 'cancelled'
                    GROUP BY garment_order_id
                ) p ON p.garment_order_id = o.id
                WHERE o.state != 'cancelled'
            )
        """ % self._table)


class GarmentProductionProgress(models.Model):
    """SQL View - Tiến độ sản xuất theo lệnh SX."""
    _name = 'garment.production.progress'
    _description = 'Tiến Độ Sản Xuất'
    _auto = False
    _order = 'completion_rate desc'

    name = fields.Char(string='Lệnh SX', readonly=True)
    garment_order_id = fields.Many2one('garment.order', string='Đơn Hàng', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Khách Hàng', readonly=True)
    style_id = fields.Many2one('garment.style', string='Mẫu May', readonly=True)
    sewing_line_id = fields.Many2one('garment.sewing.line', string='Chuyền May', readonly=True)
    planned_qty = fields.Integer(string='SL KH', readonly=True)
    completed_qty = fields.Integer(string='SL HT', readonly=True)
    defect_qty = fields.Integer(string='SL Lỗi', readonly=True)
    completion_rate = fields.Float(string='% HT', readonly=True)
    defect_rate = fields.Float(string='% Lỗi', readonly=True)
    start_date = fields.Date(string='Ngày BĐ', readonly=True)
    end_date = fields.Date(string='Ngày KT DK', readonly=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã XN'),
        ('in_progress', 'Đang SX'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', readonly=True)
    remaining_qty = fields.Integer(string='SL Còn Lại', readonly=True)
    working_days = fields.Integer(string='Số Ngày SX', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    po.id,
                    po.name,
                    po.garment_order_id,
                    po.customer_id,
                    po.style_id,
                    po.sewing_line_id,
                    po.planned_qty,
                    po.completed_qty,
                    po.defect_qty,
                    po.completion_rate,
                    CASE
                        WHEN po.completed_qty > 0
                        THEN (po.defect_qty::float / po.completed_qty * 100)
                        ELSE 0
                    END AS defect_rate,
                    po.start_date,
                    po.end_date,
                    po.state,
                    GREATEST(po.planned_qty - po.completed_qty, 0) AS remaining_qty,
                    COALESCE(d.day_count, 0) AS working_days
                FROM garment_production_order po
                LEFT JOIN (
                    SELECT production_order_id, COUNT(DISTINCT date) AS day_count
                    FROM garment_daily_output
                    GROUP BY production_order_id
                ) d ON d.production_order_id = po.id
                WHERE po.state != 'cancelled'
            )
        """ % self._table)
