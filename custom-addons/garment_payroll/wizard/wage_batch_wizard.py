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
