from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import logging
import math

_logger = logging.getLogger(__name__)


class GarmentProductionPlan(models.Model):
    _name = 'garment.production.plan'
    _description = 'Production Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    garment_order_id = fields.Many2one(
        'garment.order',
        string='Garment Order',
    )
    style_id = fields.Many2one(
        'garment.style',
        string='Style',
        required=True,
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        domain=[('customer_rank', '>', 0)],
    )
    total_quantity = fields.Integer(
        string='Tổng SL Đặt Hàng',
        required=True,
    )
    smv = fields.Float(
        string='SMV',
        required=True,
        digits=(10, 2),
    )
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình Thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn Cấp'),
    ], string='Ưu Tiên', default='1')

    date_start = fields.Date(string='Ngày Bắt Đầu', required=True)
    date_end = fields.Date(string='Ngày Kết Thúc', required=True)
    ship_date = fields.Date(string='Ngày Xuất Hàng')

    # --- Line Loadings ---
    loading_ids = fields.One2many(
        'garment.line.loading',
        'plan_id',
        string='Phân Bổ Chuyền',
    )

    total_planned = fields.Integer(
        string='Tổng SL Kế Hoạch',
        compute='_compute_planned',
        store=True,
    )
    remaining_qty = fields.Integer(
        string='SL Còn Lại',
        compute='_compute_planned',
        store=True,
    )
    total_required_days = fields.Float(
        string='Tổng Ngày Cần',
        compute='_compute_required_days',
        digits=(10, 1),
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã Xác Nhận'),
        ('in_progress', 'Đang Sản Xuất'),
        ('done', 'Hoàn Thành'),
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
                    'garment.production.plan'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Constrains
    # -------------------------------------------------------------------------
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_end < record.date_start:
                    raise ValidationError(
                        _('Ngày kết thúc phải sau ngày bắt đầu.')
                    )

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('loading_ids.planned_qty', 'total_quantity')
    def _compute_planned(self):
        for record in self:
            record.total_planned = sum(
                record.loading_ids.mapped('planned_qty')
            )
            record.remaining_qty = record.total_quantity - record.total_planned

    @api.depends('total_quantity', 'smv', 'loading_ids.daily_capacity')
    def _compute_required_days(self):
        for record in self:
            total_cap = sum(record.loading_ids.mapped('daily_capacity'))
            if total_cap > 0:
                record.total_required_days = record.total_quantity / total_cap
            else:
                record.total_required_days = 0

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_confirm(self):
        self.ensure_one()
        if not self.loading_ids:
            raise UserError(_('Vui lòng phân bổ chuyền trước khi xác nhận.'))
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.ensure_one()
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.ensure_one()
        self.write({'state': 'done'})

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_auto_schedule(self):
        """Auto-calculate end date based on capacity and quantity."""
        self.ensure_one()
        if not self.loading_ids:
            raise UserError(_('Vui lòng thêm chuyền trước khi lập lịch.'))
        total_capacity = sum(self.loading_ids.mapped('daily_capacity'))
        if total_capacity <= 0:
            raise UserError(_('Năng suất chuyền phải > 0.'))
        days_needed = math.ceil(self.total_quantity / total_capacity)
        new_end = self.date_start + timedelta(days=days_needed)
        self.write({
            'date_end': new_end,
        })
        # Distribute quantity proportionally
        distributed = 0
        loadings = list(self.loading_ids)
        for i, loading in enumerate(loadings):
            ratio = loading.daily_capacity / total_capacity
            if i < len(loadings) - 1:
                qty = int(self.total_quantity * ratio)
            else:
                qty = self.total_quantity - distributed
            distributed += qty
            loading.write({
                'planned_qty': qty,
                'date_start': self.date_start,
                'date_end': new_end,
            })

    # -------------------------------------------------------------------------
    # Cron: Deadline Auto-Alert
    # -------------------------------------------------------------------------
    @api.model
    def _cron_check_deadline_alerts(self):
        """Scheduled action: check production plans for deadline warnings.

        Creates mail.activity for plans that are:
        - Overdue (ship_date < today and not done/cancelled)
        - Approaching deadline (ship_date within 3 days)
        """
        today = fields.Date.today()
        warn_date = today + timedelta(days=3)
        activity_type = self.env.ref('mail.mail_activity_data_warning', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([], limit=1)
        if not activity_type:
            _logger.warning('No activity type found for deadline alerts')
            return

        # Plans with ship_date that are active (not done/cancelled)
        plans = self.search([
            ('ship_date', '!=', False),
            ('state', 'not in', ('done', 'cancelled')),
            ('ship_date', '<=', warn_date),
        ])

        model_id = self.env['ir.model']._get_id(self._name)
        for plan in plans:
            # Skip if activity already exists for this plan today
            existing = self.env['mail.activity'].search([
                ('res_model_id', '=', model_id),
                ('res_id', '=', plan.id),
                ('activity_type_id', '=', activity_type.id),
                ('date_deadline', '=', today),
            ], limit=1)
            if existing:
                continue

            days_left = (plan.ship_date - today).days
            if days_left < 0:
                summary = _('⚠️ QUÁ HẠN %s ngày!') % abs(days_left)
                note = _(
                    'Kế hoạch %s (Buyer: %s) đã quá hạn giao hàng %s ngày. '
                    'Ship date: %s. Vui lòng xử lý ngay!'
                ) % (plan.name, plan.buyer_id.name or '', abs(days_left),
                     plan.ship_date)
            else:
                summary = _('⏰ Còn %s ngày đến hạn giao') % days_left
                note = _(
                    'Kế hoạch %s (Buyer: %s) sẽ đến hạn giao hàng trong %s ngày. '
                    'Ship date: %s.'
                ) % (plan.name, plan.buyer_id.name or '', days_left,
                     plan.ship_date)

            user_id = plan.create_uid.id or self.env.uid
            plan.activity_schedule(
                act_type_xmlid='mail.mail_activity_data_warning',
                date_deadline=today,
                summary=summary,
                note=note,
                user_id=user_id,
            )
            _logger.info(
                'Deadline alert created for %s (ship_date=%s, days_left=%s)',
                plan.name, plan.ship_date, days_left,
            )
