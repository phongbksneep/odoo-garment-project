from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError


class WageBatchWizard(models.TransientModel):
    """Tạo bảng lương hàng loạt cho cả xưởng/phòng ban theo tháng.

    Số liệu đầu vào (lương cơ bản, phụ cấp, đơn giá OT, người phụ thuộc...)
    được chép từ phiếu lương gần nhất của từng nhân viên — đúng thực tế
    "tháng sau giống tháng trước", chỉ sửa chỗ khác biệt.
    """
    _name = 'garment.wage.batch.wizard'
    _description = 'Tạo Bảng Lương Hàng Loạt'

    month = fields.Selection([
        ('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
        ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
        ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng', required=True,
       default=lambda self: '%02d' % date.today().month)
    year = fields.Integer(
        string='Năm', required=True,
        default=lambda self: date.today().year,
    )
    department_ids = fields.Many2many(
        'hr.department', string='Phòng Ban',
        help='Để trống = toàn bộ nhân viên đang làm việc',
    )
    auto_calculate = fields.Boolean(
        string='Tính Lương Ngay',
        default=True,
        help='Tự động bấm Tính Lương cho các phiếu vừa tạo.',
    )

    # Các trường chép từ phiếu lương tháng trước của từng nhân viên
    _CARRY_FIELDS = [
        'base_salary', 'working_days', 'ot_rate', 'hourly_rate',
        'insurance_base', 'apply_insurance', 'dependent_count',
        'personal_deduction', 'allowance_attendance', 'allowance_lunch',
        'allowance_transport', 'allowance_phone', 'allowance',
    ]

    def action_generate(self):
        self.ensure_one()
        Wage = self.env['garment.wage.calculation']
        employees = self.env['hr.employee'].search(
            [('department_id', 'in', self.department_ids.ids)]
            if self.department_ids else [])
        if not employees:
            raise UserError(_('Không có nhân viên nào phù hợp.'))
        existing = Wage.search([
            ('month', '=', self.month),
            ('year', '=', self.year),
            ('employee_id', 'in', employees.ids),
        ]).employee_id
        todo = employees - existing
        if not todo:
            raise UserError(_(
                'Tất cả nhân viên đã có phiếu lương tháng %s/%d.')
                % (self.month, self.year))

        vals_list = []
        for emp in todo:
            vals = {
                'employee_id': emp.id,
                'month': self.month,
                'year': self.year,
            }
            previous = Wage.search(
                [('employee_id', '=', emp.id)],
                order='year desc, month desc', limit=1)
            if previous:
                for fname in self._CARRY_FIELDS:
                    vals[fname] = previous[fname]
            vals_list.append(vals)
        wages = Wage.create(vals_list)
        if self.auto_calculate:
            wages.action_calculate()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bảng Lương %s/%d') % (self.month, self.year),
            'res_model': 'garment.wage.calculation',
            'view_mode': 'list,form',
            'domain': [('id', 'in', wages.ids)],
        }


class WorkerOutputCopyWizard(models.TransientModel):
    """Chép danh sách sản lượng của ngày làm việc trước sang ngày mới
    (SL = 0) — thống kê chỉ điền số lượng, khỏi chọn lại người/mã/đơn giá."""
    _name = 'garment.worker.output.copy.wizard'
    _description = 'Chép Sản Lượng Ngày Trước'

    date = fields.Date(
        string='Ngày Mới', required=True, default=fields.Date.today)
    sewing_line_id = fields.Many2one(
        'garment.sewing.line', string='Chuyền May',
        help='Để trống = tất cả các chuyền',
    )

    def action_copy(self):
        self.ensure_one()
        Output = self.env['garment.worker.output']
        domain = [('date', '<', self.date)]
        if self.sewing_line_id:
            domain.append(('sewing_line_id', '=', self.sewing_line_id.id))
        last = Output.search(domain, order='date desc', limit=1)
        if not last:
            raise UserError(_('Không tìm thấy sản lượng ngày trước để chép.'))
        source_domain = [('date', '=', last.date)]
        if self.sewing_line_id:
            source_domain.append(
                ('sewing_line_id', '=', self.sewing_line_id.id))
        sources = Output.search(source_domain)
        # Bỏ người đã có dòng trong ngày mới
        existing = Output.search([
            ('date', '=', self.date),
            ('employee_id', 'in', sources.employee_id.ids),
        ]).employee_id
        new_rows = Output.create([{
            'date': self.date,
            'employee_id': src.employee_id.id,
            'sewing_line_id': src.sewing_line_id.id,
            'style_id': src.style_id.id,
            'piece_rate_id': src.piece_rate_id.id,
            'quantity': 0,
        } for src in sources if src.employee_id not in existing])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sản Lượng %s') % self.date,
            'res_model': 'garment.worker.output',
            'view_mode': 'list,form',
            'domain': [('id', 'in', new_rows.ids)],
        }


class WorkerOutputPasteWizard(models.TransientModel):
    """Dán sản lượng cuối ca từ Excel: mỗi dòng "Mã NV (hoặc tên) <tab> SL"."""
    _name = 'garment.worker.output.paste.wizard'
    _description = 'Dán Sản Lượng Từ Excel'

    date = fields.Date(
        string='Ngày', required=True, default=fields.Date.today)
    sewing_line_id = fields.Many2one(
        'garment.sewing.line', string='Chuyền May')
    style_id = fields.Many2one(
        'garment.style', string='Mã Hàng', required=True)
    piece_rate_id = fields.Many2one(
        'garment.piece.rate', string='Đơn Giá', required=True,
        domain="[('style_id', '=', style_id)]")
    paste_text = fields.Text(
        string='Dán Từ Excel', required=True,
        help='Mỗi dòng: Mã nhân viên (hoặc tên) [tab] số lượng.',
    )

    def action_import(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        vals_list = []
        errors = []
        for raw in self.paste_text.splitlines():
            if not raw.strip():
                continue
            sep = '\t' if '\t' in raw else ';'
            cells = [c.strip() for c in raw.split(sep)]
            if len(cells) < 2:
                errors.append(_('Dòng "%s" thiếu số lượng.') % raw)
                continue
            emp = Employee.search(
                ['|', ('employee_code', '=ilike', cells[0]),
                 ('name', '=ilike', cells[0])], limit=1)
            if not emp:
                errors.append(
                    _('Không tìm thấy nhân viên "%s".') % cells[0])
                continue
            try:
                qty = int(float(cells[1].replace(',', '')))
            except ValueError:
                errors.append(
                    _('SL "%s" của %s không phải là số.')
                    % (cells[1], cells[0]))
                continue
            vals_list.append({
                'date': self.date,
                'employee_id': emp.id,
                'sewing_line_id': self.sewing_line_id.id,
                'style_id': self.style_id.id,
                'piece_rate_id': self.piece_rate_id.id,
                'quantity': qty,
            })
        if errors:
            raise UserError('\n'.join(errors))
        if not vals_list:
            raise UserError(_('Không có dòng hợp lệ nào để nhập.'))
        rows = self.env['garment.worker.output'].create(vals_list)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sản Lượng %s') % self.date,
            'res_model': 'garment.worker.output',
            'view_mode': 'list,form',
            'domain': [('id', 'in', rows.ids)],
        }
