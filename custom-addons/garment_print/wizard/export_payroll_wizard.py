import base64
import io
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class ExportPayrollWizard(models.TransientModel):
    _name = 'garment.export.payroll.wizard'
    _description = 'Xuất Bảng Lương Excel'

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
        help='Để trống = tất cả phòng ban',
    )
    file_data = fields.Binary(string='File Excel', readonly=True)
    file_name = fields.Char(string='Tên File', readonly=True)

    def action_export(self):
        """Generate payroll Excel file."""
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_('Thư viện xlsxwriter chưa được cài đặt!'))

        domain = [
            ('month', '=', self.month),
            ('year', '=', self.year),
        ]
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        wages = self.env['garment.wage.calculation'].search(domain, order='department_id, employee_id')
        if not wages:
            raise UserError(_('Không tìm thấy dữ liệu lương cho tháng %s/%d!') % (self.month, self.year))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Bảng Lương')

        # --- Formats ---
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
        })
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#4CAF50', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
        })
        number_fmt = workbook.add_format({
            'num_format': '#,##0', 'border': 1, 'align': 'right',
        })
        text_fmt = workbook.add_format({'border': 1, 'align': 'left'})
        total_fmt = workbook.add_format({
            'bold': True, 'num_format': '#,##0', 'border': 1, 'align': 'right',
            'bg_color': '#FFF9C4',
        })
        total_text_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#FFF9C4',
        })

        month_name = dict(self._fields['month'].selection).get(self.month, '')
        # Title
        sheet.merge_range('A1:N1', 'BẢNG LƯƠNG %s NĂM %d' % (month_name.upper(), self.year), title_fmt)
        sheet.set_row(0, 30)

        # Headers
        headers = [
            'STT', 'Mã NV', 'Họ Tên', 'Phòng Ban',
            'Ngày Công', 'Lương CB', 'Lương Ngày Công',
            'Tiền Khoán', 'Tiền Tăng Ca', 'Phụ Cấp',
            'BHXH (10.5%)', 'Thuế TNCN', 'Tổng Thu Nhập', 'Thực Lĩnh',
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header, header_fmt)

        # Column widths
        widths = [5, 12, 25, 20, 10, 15, 15, 15, 15, 12, 15, 12, 15, 15]
        for col, w in enumerate(widths):
            sheet.set_column(col, col, w)

        # Data rows
        row = 3
        totals = [0] * 10  # For summing numeric columns
        for idx, wage in enumerate(wages, 1):
            sheet.write(row, 0, idx, text_fmt)
            sheet.write(row, 1, wage.employee_id.barcode or '', text_fmt)
            sheet.write(row, 2, wage.employee_id.name or '', text_fmt)
            sheet.write(row, 3, wage.department_id.name or '', text_fmt)
            sheet.write(row, 4, wage.actual_days or 0, number_fmt)
            sheet.write(row, 5, wage.base_salary or 0, number_fmt)
            sheet.write(row, 6, wage.base_amount or 0, number_fmt)
            sheet.write(row, 7, wage.piece_rate_amount or 0, number_fmt)
            sheet.write(row, 8, wage.ot_amount or 0, number_fmt)
            sheet.write(row, 9, wage.total_allowance or 0, number_fmt)
            sheet.write(row, 10, wage.total_insurance or 0, number_fmt)
            sheet.write(row, 11, wage.pit_amount or 0, number_fmt)
            sheet.write(row, 12, wage.total_wage or 0, number_fmt)
            sheet.write(row, 13, wage.net_pay or 0, number_fmt)

            # Accumulate totals
            values = [
                wage.actual_days, wage.base_salary, wage.base_amount,
                wage.piece_rate_amount, wage.ot_amount, wage.total_allowance,
                wage.total_insurance, wage.pit_amount, wage.total_wage, wage.net_pay,
            ]
            for i, v in enumerate(values):
                totals[i] += (v or 0)
            row += 1

        # Total row
        sheet.write(row, 0, '', total_text_fmt)
        sheet.write(row, 1, '', total_text_fmt)
        sheet.write(row, 2, 'TỔNG CỘNG', total_text_fmt)
        sheet.write(row, 3, '%d người' % len(wages), total_text_fmt)
        for i, total_val in enumerate(totals):
            sheet.write(row, 4 + i, total_val, total_fmt)

        workbook.close()
        output.seek(0)

        file_name = 'BangLuong_%s_%d.xlsx' % (self.month, self.year)
        self.write({
            'file_data': base64.b64encode(output.read()),
            'file_name': file_name,
        })
        output.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'name': _('Tải Bảng Lương Excel'),
        }
