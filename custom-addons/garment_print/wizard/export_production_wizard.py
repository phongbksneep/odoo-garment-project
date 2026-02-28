import base64
import io
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class ExportProductionWizard(models.TransientModel):
    _name = 'garment.export.production.wizard'
    _description = 'Xuất Báo Cáo Sản Xuất Excel'

    date_from = fields.Date(
        string='Từ Ngày', required=True,
        default=lambda self: date.today().replace(day=1),
    )
    date_to = fields.Date(
        string='Đến Ngày', required=True,
        default=fields.Date.today,
    )
    sewing_line_ids = fields.Many2many(
        'garment.sewing.line', string='Chuyền May',
        help='Để trống = tất cả chuyền',
    )
    file_data = fields.Binary(string='File Excel', readonly=True)
    file_name = fields.Char(string='Tên File', readonly=True)

    def action_export(self):
        """Generate production summary Excel file."""
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_('Thư viện xlsxwriter chưa được cài đặt!'))

        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.sewing_line_ids:
            domain.append(('sewing_line_id', 'in', self.sewing_line_ids.ids))

        outputs = self.env['garment.daily.output'].search(
            domain, order='date, sewing_line_id'
        )
        if not outputs:
            raise UserError(_('Không tìm thấy dữ liệu sản lượng trong khoảng thời gian này!'))

        output_file = io.BytesIO()
        workbook = xlsxwriter.Workbook(output_file, {'in_memory': True})
        sheet = workbook.add_worksheet('Sản Lượng')

        # --- Formats ---
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
        })
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#2196F3', 'font_color': 'white',
            'border': 1, 'align': 'center', 'text_wrap': True,
        })
        number_fmt = workbook.add_format({
            'num_format': '#,##0', 'border': 1, 'align': 'right',
        })
        pct_fmt = workbook.add_format({
            'num_format': '0.0%', 'border': 1, 'align': 'right',
        })
        date_fmt = workbook.add_format({
            'num_format': 'dd/mm/yyyy', 'border': 1, 'align': 'center',
        })
        text_fmt = workbook.add_format({'border': 1})
        total_fmt = workbook.add_format({
            'bold': True, 'num_format': '#,##0', 'border': 1, 'bg_color': '#FFF9C4',
        })
        total_text_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'bg_color': '#FFF9C4', 'align': 'center',
        })
        total_pct_fmt = workbook.add_format({
            'bold': True, 'num_format': '0.0%', 'border': 1, 'bg_color': '#FFF9C4',
        })

        # Title
        sheet.merge_range(
            'A1:J1',
            'BÁO CÁO SẢN LƯỢNG: %s → %s' % (
                self.date_from.strftime('%d/%m/%Y'),
                self.date_to.strftime('%d/%m/%Y'),
            ),
            title_fmt,
        )
        sheet.set_row(0, 28)

        # Headers
        headers = [
            'STT', 'Ngày', 'Chuyền May', 'Lệnh SX', 'Mã Hàng', 'Ca',
            'Mục Tiêu', 'Đạt', 'Lỗi', 'Hiệu Suất',
        ]
        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_fmt)

        widths = [5, 12, 18, 18, 18, 12, 10, 10, 8, 10]
        for col, w in enumerate(widths):
            sheet.set_column(col, col, w)

        # Data
        row = 3
        sum_target = sum_output = sum_defect = 0
        shift_labels = dict(outputs._fields['shift'].selection) if 'shift' in outputs._fields else {}
        for idx, rec in enumerate(outputs, 1):
            sheet.write(row, 0, idx, text_fmt)
            sheet.write(row, 1, rec.date.strftime('%d/%m/%Y') if rec.date else '', date_fmt)
            sheet.write(row, 2, rec.sewing_line_id.name if rec.sewing_line_id else '', text_fmt)
            sheet.write(row, 3, rec.production_order_id.name if rec.production_order_id else '', text_fmt)
            style_name = ''
            if hasattr(rec, 'style_id') and rec.style_id:
                style_name = rec.style_id.name
            elif rec.production_order_id and rec.production_order_id.style_id:
                style_name = rec.production_order_id.style_id.name
            sheet.write(row, 4, style_name, text_fmt)
            sheet.write(row, 5, shift_labels.get(rec.shift, rec.shift) if hasattr(rec, 'shift') else '', text_fmt)
            target = rec.target_qty if hasattr(rec, 'target_qty') else 0
            output_qty = rec.output_qty if hasattr(rec, 'output_qty') else 0
            defect_qty = rec.defect_qty if hasattr(rec, 'defect_qty') else 0
            sheet.write(row, 6, target, number_fmt)
            sheet.write(row, 7, output_qty, number_fmt)
            sheet.write(row, 8, defect_qty, number_fmt)
            eff = (output_qty / target) if target else 0
            sheet.write(row, 9, eff, pct_fmt)
            sum_target += target
            sum_output += output_qty
            sum_defect += defect_qty
            row += 1

        # Totals
        sheet.write(row, 0, '', total_text_fmt)
        sheet.write(row, 1, '', total_text_fmt)
        sheet.write(row, 2, 'TỔNG CỘNG', total_text_fmt)
        sheet.write(row, 3, '', total_text_fmt)
        sheet.write(row, 4, '', total_text_fmt)
        sheet.write(row, 5, '%d dòng' % len(outputs), total_text_fmt)
        sheet.write(row, 6, sum_target, total_fmt)
        sheet.write(row, 7, sum_output, total_fmt)
        sheet.write(row, 8, sum_defect, total_fmt)
        total_eff = (sum_output / sum_target) if sum_target else 0
        sheet.write(row, 9, total_eff, total_pct_fmt)

        workbook.close()
        output_file.seek(0)

        file_name = 'SanLuong_%s_%s.xlsx' % (
            self.date_from.strftime('%Y%m%d'),
            self.date_to.strftime('%Y%m%d'),
        )
        self.write({
            'file_data': base64.b64encode(output_file.read()),
            'file_name': file_name,
        })
        output_file.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'name': _('Tải Báo Cáo Sản Xuất Excel'),
        }
