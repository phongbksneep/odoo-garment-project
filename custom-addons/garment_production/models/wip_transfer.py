from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GarmentWipTransfer(models.Model):
    """Phiếu giao nhận bán thành phẩm giữa các công đoạn
    (cắt → may → hoàn thiện → đóng gói)."""
    _name = 'garment.wip.transfer'
    _description = 'Phiếu Giao Nhận Bán Thành Phẩm'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    _name_uniq = models.Constraint(
        'UNIQUE(name)', 'Số phiếu giao nhận phải là duy nhất!')

    STAGES = [
        ('cutting', 'Tổ Cắt'),
        ('sewing', 'Chuyền May'),
        ('finishing', 'Hoàn Thiện'),
        ('packing', 'Đóng Gói'),
    ]

    name = fields.Char(
        string='Số Phiếu', required=True, copy=False, readonly=True,
        default='New', index=True)
    date = fields.Date(
        string='Ngày Giao', required=True, default=fields.Date.today)
    garment_order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng May', required=True,
        ondelete='restrict')
    production_order_id = fields.Many2one(
        'garment.production.order', string='Lệnh Sản Xuất',
        domain="[('garment_order_id', '=', garment_order_id)]")
    style_id = fields.Many2one(
        related='garment_order_id.style_id', store=True)
    from_stage = fields.Selection(
        STAGES, string='Từ Công Đoạn', required=True, default='cutting')
    to_stage = fields.Selection(
        STAGES, string='Đến Công Đoạn', required=True, default='sewing')
    quantity = fields.Integer(string='Số Lượng (sp)', required=True)
    bundle_note = fields.Char(
        string='Số Bó / Ghi Chú BTP',
        help='VD: Bó 12-18, size M màu đen')
    giver_id = fields.Many2one(
        'hr.employee', string='Người Giao', required=True)
    receiver_id = fields.Many2one(
        'hr.employee', string='Người Nhận')
    note = fields.Text(string='Ghi Chú')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('transferred', 'Đã Giao'),
        ('received', 'Đã Nhận'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'garment.wip.transfer') or 'New'
        return super().create(vals_list)

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_('Số lượng phải lớn hơn 0.'))

    @api.constrains('from_stage', 'to_stage')
    def _check_stages(self):
        for rec in self:
            if rec.from_stage == rec.to_stage:
                raise ValidationError(_(
                    'Công đoạn giao và nhận phải khác nhau.'))

    def action_transfer(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Chỉ phiếu Nháp mới được giao.'))
        self.write({'state': 'transferred'})

    def action_receive(self):
        for rec in self:
            if rec.state != 'transferred':
                raise UserError(_('Phiếu phải Đã Giao mới được xác nhận nhận.'))
            if not rec.receiver_id:
                raise UserError(_('Phải chọn người nhận trước.'))
        self.write({'state': 'received'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'received':
                raise UserError(_('Không thể hủy phiếu đã nhận.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'received':
                raise UserError(_(
                    'Không thể đưa phiếu đã nhận về Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state == 'received':
                raise UserError(_(
                    'Không thể xóa phiếu giao nhận %s đã nhận.', rec.name))
        return super().unlink()
