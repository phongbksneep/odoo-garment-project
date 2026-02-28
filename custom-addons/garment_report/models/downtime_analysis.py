from odoo import models, fields, tools


class GarmentDowntimeAnalysis(models.Model):
    """SQL View: Machine downtime analytics per maintenance request.

    Aggregates maintenance data to provide insights on downtime duration,
    repair efficiency (MTTR), costs, and breakdown patterns by machine,
    machine type, technician, and period.
    """
    _name = 'garment.downtime.analysis'
    _description = 'Downtime Analysis'
    _auto = False
    _order = 'downtime_hours desc'

    # --- Dimensions ---
    request_id = fields.Many2one(
        'garment.maintenance.request', string='Yêu Cầu BT', readonly=True,
    )
    machine_id = fields.Many2one(
        'garment.machine', string='Máy', readonly=True,
    )
    machine_type = fields.Selection([
        ('lockstitch', 'Lockstitch'),
        ('overlock', 'Overlock'),
        ('flatlock', 'Flatlock'),
        ('bartack', 'Bartack'),
        ('buttonhole', 'Buttonhole'),
        ('button_attach', 'Button Attach'),
        ('zigzag', 'Zigzag'),
        ('cutting', 'Cutting'),
        ('pressing', 'Pressing'),
        ('other', 'Other'),
    ], string='Loại Máy', readonly=True)
    sewing_line_id = fields.Many2one(
        'garment.sewing.line', string='Chuyền May', readonly=True,
    )
    technician_id = fields.Many2one(
        'hr.employee', string='Kỹ Thuật Viên', readonly=True,
    )
    request_type = fields.Selection([
        ('preventive', 'Bảo Trì Định Kỳ'),
        ('corrective', 'Sửa Chữa'),
        ('breakdown', 'Hỏng Máy'),
    ], string='Loại Yêu Cầu', readonly=True)
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình Thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn Cấp'),
    ], string='Độ Ưu Tiên', readonly=True)
    state = fields.Char(string='Trạng Thái', readonly=True)

    # --- Time ---
    request_date = fields.Datetime(
        string='Ngày Yêu Cầu', readonly=True,
    )
    completion_date = fields.Datetime(
        string='Ngày Hoàn Thành', readonly=True,
    )

    # --- Metrics ---
    downtime_hours = fields.Float(
        string='Thời Gian Dừng (h)', readonly=True, digits=(10, 1),
    )
    repair_hours = fields.Float(
        string='Thời Gian Sửa (h)',
        readonly=True,
        digits=(10, 1),
        help='completion_date - request_date (giờ)',
    )
    cost = fields.Float(
        string='Chi Phí (VNĐ)', readonly=True, digits=(10, 2),
    )
    is_breakdown = fields.Integer(
        string='Là Hỏng Máy', readonly=True,
        help='1 nếu loại = breakdown, 0 nếu không',
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    mr.id AS id,
                    mr.id AS request_id,
                    mr.machine_id AS machine_id,
                    m.machine_type AS machine_type,
                    m.sewing_line_id AS sewing_line_id,
                    mr.technician_id AS technician_id,
                    mr.request_type AS request_type,
                    mr.priority AS priority,
                    mr.state AS state,

                    -- Time
                    mr.request_date AS request_date,
                    mr.completion_date AS completion_date,

                    -- Metrics
                    COALESCE(mr.downtime_hours, 0) AS downtime_hours,
                    CASE
                        WHEN mr.completion_date IS NOT NULL
                             AND mr.request_date IS NOT NULL
                        THEN EXTRACT(EPOCH FROM
                             (mr.completion_date - mr.request_date)) / 3600.0
                        ELSE 0
                    END AS repair_hours,
                    COALESCE(mr.cost, 0) AS cost,
                    CASE
                        WHEN mr.request_type = 'breakdown' THEN 1
                        ELSE 0
                    END AS is_breakdown

                FROM garment_maintenance_request mr
                JOIN garment_machine m ON m.id = mr.machine_id
            )
        """ % self._table)
