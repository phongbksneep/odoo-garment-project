from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import math


class GarmentCapacityPlanning(models.Model):
    _name = 'garment.capacity.planning'
    _description = 'Capacity Planning Nâng Cao'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Mã Kế Hoạch',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Đơn Hàng May',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Mã Hàng',
        required=True,
    )
    sam = fields.Float(
        string='SAM (Phút)',
        required=True,
        digits=(10, 2),
        help='Standard Allowed Minutes - Thời gian tiêu chuẩn để may 1 sản phẩm (phút)',
    )
    total_quantity = fields.Integer(
        string='Tổng SL Đặt Hàng',
        required=True,
    )
    working_minutes_per_day = fields.Integer(
        string='Phút Làm Việc / Ngày',
        default=480,
        required=True,
        help='Thời gian làm việc tiêu chuẩn (mặc định: 480 phút = 8 giờ)',
    )
    break_minutes = fields.Integer(
        string='Phút Nghỉ / Ngày',
        default=60,
        help='Tổng thời gian nghỉ giải lao trong ngày',
    )
    overtime_minutes = fields.Integer(
        string='Phút Tăng Ca / Ngày',
        default=0,
        help='Thời gian tăng ca bổ sung',
    )
    available_minutes = fields.Integer(
        string='Phút Khả Dụng / Ngày',
        compute='_compute_available_minutes',
        store=True,
    )
    ship_date = fields.Date(
        string='Ngày Xuất Hàng',
    )
    available_days = fields.Integer(
        string='Số Ngày Có Thể SX',
        compute='_compute_available_days',
    )

    # --- Capacity lines ---
    line_ids = fields.One2many(
        'garment.capacity.line',
        'planning_id',
        string='Phân Bổ Chuyền',
    )

    # --- Summary ---
    total_daily_output = fields.Integer(
        string='Tổng Năng Suất / Ngày',
        compute='_compute_summary',
        store=True,
    )
    total_hourly_output = fields.Float(
        string='Tổng Năng Suất / Giờ',
        compute='_compute_summary',
        store=True,
        digits=(10, 1),
    )
    total_workers = fields.Integer(
        string='Tổng Số CN',
        compute='_compute_summary',
        store=True,
    )
    required_days = fields.Float(
        string='Số Ngày Cần',
        compute='_compute_summary',
        store=True,
        digits=(10, 1),
    )
    can_meet_deadline = fields.Boolean(
        string='Đạt Tiến Độ?',
        compute='_compute_can_meet_deadline',
        store=True,
    )
    utilization_rate = fields.Float(
        string='Tỷ Lệ Sử Dụng (%)',
        compute='_compute_summary',
        store=True,
        digits=(10, 1),
    )
    pieces_per_worker_day = fields.Float(
        string='SP / CN / Ngày',
        compute='_compute_summary',
        store=True,
        digits=(10, 1),
    )
    bottleneck_line_id = fields.Many2one(
        'garment.capacity.line',
        string='Chuyền Thắt Cổ Chai',
        compute='_compute_summary',
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('simulated', 'Đã Tính Toán'),
        ('approved', 'Đã Duyệt'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    notes = fields.Text(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.capacity.planning'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Onchange
    # -------------------------------------------------------------------------
    @api.onchange('style_id')
    def _onchange_style_id(self):
        if self.style_id and self.style_id.sam:
            self.sam = self.style_id.sam

    @api.onchange('garment_order_id')
    def _onchange_garment_order_id(self):
        if self.garment_order_id:
            self.style_id = self.garment_order_id.style_id
            self.total_quantity = self.garment_order_id.total_qty
            self.ship_date = self.garment_order_id.delivery_date
            if self.garment_order_id.style_id.sam:
                self.sam = self.garment_order_id.style_id.sam

    # -------------------------------------------------------------------------
    # Constrains
    # -------------------------------------------------------------------------
    @api.constrains('sam')
    def _check_sam(self):
        for record in self:
            if record.sam <= 0:
                raise ValidationError(_('SAM phải lớn hơn 0!'))

    @api.constrains('total_quantity')
    def _check_quantity(self):
        for record in self:
            if record.total_quantity <= 0:
                raise ValidationError(_('Số lượng đặt hàng phải lớn hơn 0!'))

    @api.constrains('working_minutes_per_day', 'break_minutes')
    def _check_minutes(self):
        for record in self:
            if record.working_minutes_per_day <= 0:
                raise ValidationError(
                    _('Phút làm việc / ngày phải lớn hơn 0!')
                )
            if record.break_minutes < 0:
                raise ValidationError(
                    _('Phút nghỉ không được âm!')
                )
            net = (record.working_minutes_per_day - record.break_minutes
                   + record.overtime_minutes)
            if net <= 0:
                raise ValidationError(
                    _('Tổng phút khả dụng (làm việc - nghỉ + tăng ca) phải > 0!')
                )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('working_minutes_per_day', 'break_minutes', 'overtime_minutes')
    def _compute_available_minutes(self):
        for record in self:
            record.available_minutes = (
                record.working_minutes_per_day
                - record.break_minutes
                + record.overtime_minutes
            )

    def _compute_available_days(self):
        today = fields.Date.today()
        for record in self:
            if record.ship_date and record.ship_date > today:
                record.available_days = (record.ship_date - today).days
            else:
                record.available_days = 0

    @api.depends(
        'line_ids.daily_output', 'line_ids.hourly_output',
        'line_ids.worker_count', 'line_ids.pieces_per_worker',
        'total_quantity', 'available_minutes',
    )
    def _compute_summary(self):
        for record in self:
            lines = record.line_ids
            total_daily = sum(lines.mapped('daily_output'))
            total_hourly = sum(lines.mapped('hourly_output'))
            total_workers = sum(lines.mapped('worker_count'))

            record.total_daily_output = total_daily
            record.total_hourly_output = total_hourly
            record.total_workers = total_workers

            if total_daily > 0:
                record.required_days = math.ceil(
                    record.total_quantity / total_daily
                )
            else:
                record.required_days = 0

            if total_workers > 0 and total_daily > 0:
                record.pieces_per_worker_day = total_daily / total_workers
            else:
                record.pieces_per_worker_day = 0

            # Utilization: actual needed minutes vs total available
            total_sam_needed = record.total_quantity * record.sam
            total_available = (
                total_workers
                * record.available_minutes
                * record.required_days
            ) if record.required_days > 0 else 0
            if total_available > 0:
                record.utilization_rate = (
                    total_sam_needed / total_available * 100
                )
            else:
                record.utilization_rate = 0

            # Bottleneck: line with lowest daily_output per worker
            bottleneck = False
            min_ppw = float('inf')
            for line in lines:
                if line.pieces_per_worker > 0 and line.pieces_per_worker < min_ppw:
                    min_ppw = line.pieces_per_worker
                    bottleneck = line
            record.bottleneck_line_id = bottleneck.id if bottleneck else False

    @api.depends('required_days', 'ship_date')
    def _compute_can_meet_deadline(self):
        today = fields.Date.today()
        for record in self:
            if record.ship_date and record.required_days > 0:
                needed_date = today + timedelta(days=int(record.required_days))
                record.can_meet_deadline = needed_date <= record.ship_date
            else:
                record.can_meet_deadline = False

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_simulate(self):
        """Tính toán công suất tự động cho tất cả chuyền."""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(
                _('Vui lòng thêm ít nhất 1 chuyền trước khi tính toán!')
            )
        if self.sam <= 0:
            raise UserError(_('SAM phải lớn hơn 0!'))
        # Trigger recompute
        self.line_ids._compute_capacity()
        self.write({'state': 'simulated'})

    def action_approve(self):
        self.ensure_one()
        if self.state != 'simulated':
            raise UserError(
                _('Phải tính toán trước khi duyệt!')
            )
        self.write({'state': 'approved'})

    def action_create_production_plan(self):
        """Tạo kế hoạch sản xuất từ capacity planning."""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Chưa có chuyền nào được phân bổ!'))

        today = fields.Date.today()
        plan = self.env['garment.production.plan'].create({
            'garment_order_id': self.garment_order_id.id if self.garment_order_id else False,
            'style_id': self.style_id.id,
            'buyer_id': (
                self.garment_order_id.customer_id.id
                if self.garment_order_id else False
            ),
            'total_quantity': self.total_quantity,
            'smv': self.sam,
            'date_start': today,
            'date_end': today + timedelta(days=int(self.required_days) or 30),
            'ship_date': self.ship_date,
        })

        # Create line loadings from capacity lines
        total_daily = self.total_daily_output or 1
        distributed = 0
        cap_lines = list(self.line_ids)
        for i, cl in enumerate(cap_lines):
            ratio = cl.daily_output / total_daily if total_daily else 0
            if i < len(cap_lines) - 1:
                qty = int(self.total_quantity * ratio)
            else:
                qty = self.total_quantity - distributed
            distributed += qty

            self.env['garment.line.loading'].create({
                'plan_id': plan.id,
                'sewing_line_id': cl.sewing_line_id.id,
                'target_efficiency': cl.target_efficiency,
                'planned_qty': qty,
                'date_start': today,
                'date_end': today + timedelta(
                    days=int(self.required_days) or 30
                ),
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'garment.production.plan',
            'res_id': plan.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})


class GarmentCapacityLine(models.Model):
    _name = 'garment.capacity.line'
    _description = 'Chi Tiết Capacity Planning'
    _order = 'daily_output desc'

    planning_id = fields.Many2one(
        'garment.capacity.planning',
        string='Capacity Planning',
        required=True,
        ondelete='cascade',
    )
    sewing_line_id = fields.Many2one(
        'garment.sewing.line',
        string='Chuyền May',
        required=True,
    )
    worker_count = fields.Integer(
        string='Số Công Nhân',
        compute='_compute_worker_count',
        store=True,
        readonly=False,
        help='Mặc định lấy từ chuyền, có thể điều chỉnh',
    )
    target_efficiency = fields.Float(
        string='Hiệu Suất Mục Tiêu (%)',
        default=65.0,
        digits=(10, 1),
    )

    # --- Computed capacity ---
    sam = fields.Float(
        string='SAM',
        related='planning_id.sam',
    )
    available_minutes = fields.Integer(
        string='Phút Khả Dụng',
        related='planning_id.available_minutes',
    )
    daily_output = fields.Integer(
        string='Năng Suất / Ngày',
        compute='_compute_capacity',
        store=True,
    )
    hourly_output = fields.Float(
        string='Năng Suất / Giờ',
        compute='_compute_capacity',
        store=True,
        digits=(10, 1),
    )
    pieces_per_worker = fields.Float(
        string='SP / CN / Ngày',
        compute='_compute_capacity',
        store=True,
        digits=(10, 1),
    )
    required_days = fields.Float(
        string='Ngày Cần (riêng)',
        compute='_compute_capacity',
        store=True,
        digits=(10, 1),
        help='Số ngày cần nếu chỉ dùng chuyền này',
    )
    line_share_pct = fields.Float(
        string='Tỷ Trọng (%)',
        compute='_compute_line_share',
        store=True,
        digits=(10, 1),
        help='Phần trăm đóng góp năng suất so với tổng',
    )

    notes = fields.Char(string='Ghi Chú')

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('sewing_line_id.worker_count')
    def _compute_worker_count(self):
        for line in self:
            if line.sewing_line_id:
                line.worker_count = line.sewing_line_id.worker_count
            else:
                line.worker_count = 0

    @api.depends(
        'worker_count', 'target_efficiency',
        'planning_id.sam', 'planning_id.available_minutes',
        'planning_id.total_quantity',
    )
    def _compute_capacity(self):
        for line in self:
            sam = line.planning_id.sam if line.planning_id else 0
            avail = line.planning_id.available_minutes if line.planning_id else 0
            total_qty = (
                line.planning_id.total_quantity if line.planning_id else 0
            )

            if sam > 0 and line.worker_count > 0 and avail > 0:
                eff = line.target_efficiency / 100.0
                # Daily output = (workers × available_minutes × efficiency) / SAM
                line.daily_output = int(
                    (line.worker_count * avail * eff) / sam
                )
                # Hourly output = (workers × 60 × efficiency) / SAM
                line.hourly_output = round(
                    (line.worker_count * 60 * eff) / sam, 1
                )
                # Pieces per worker per day
                line.pieces_per_worker = round(
                    line.daily_output / line.worker_count, 1
                ) if line.worker_count > 0 else 0
                # Required days if only this line
                line.required_days = math.ceil(
                    total_qty / line.daily_output
                ) if line.daily_output > 0 else 0
            else:
                line.daily_output = 0
                line.hourly_output = 0
                line.pieces_per_worker = 0
                line.required_days = 0

    @api.depends('daily_output', 'planning_id.line_ids.daily_output')
    def _compute_line_share(self):
        for line in self:
            total_daily = sum(
                line.planning_id.line_ids.mapped('daily_output')
            ) if line.planning_id else 0
            if total_daily > 0 and line.daily_output > 0:
                line.line_share_pct = round(
                    line.daily_output / total_daily * 100, 1
                )
            else:
                line.line_share_pct = 0
