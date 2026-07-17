from odoo import models, fields, _
from odoo.exceptions import UserError


class OrderMatrixImportWizard(models.TransientModel):
    """Dán ma trận size/màu từ Excel vào đơn hàng.

    Định dạng (copy thẳng từ Excel, phân cách tab):
        (ô trống)   S     M     L     XL
        Đen         100   200   200   100
        Trắng       50    150   150   50
    Dòng đầu là size, cột đầu là màu, các ô là số lượng.
    """
    _name = 'garment.order.matrix.import.wizard'
    _description = 'Nhập Bảng Size/Màu Từ Excel'

    order_id = fields.Many2one(
        'garment.order', string='Đơn Hàng', required=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    matrix_text = fields.Text(
        string='Dán Bảng Từ Excel',
        required=True,
        help='Copy vùng bảng trong Excel (gồm dòng size và cột màu) '
             'rồi dán vào đây.',
    )
    create_missing = fields.Boolean(
        string='Tự Tạo Màu/Size Chưa Có',
        default=True,
    )

    def _split(self, line):
        # Excel dán vào là tab; hỗ trợ thêm dấu ; cho người gõ tay
        sep = '\t' if '\t' in line else ';'
        return [cell.strip() for cell in line.split(sep)]

    def _resolve(self, model, value):
        """Tìm theo mã hoặc tên (không phân biệt hoa thường)."""
        record = model.search(
            ['|', ('code', '=ilike', value), ('name', '=ilike', value)],
            limit=1)
        if record:
            return record
        if not self.create_missing:
            raise UserError(_(
                'Không tìm thấy "%s" trong danh mục %s. Tạo trước hoặc '
                'bật "Tự Tạo Màu/Size Chưa Có".', value, model._description))
        vals = {'name': value, 'code': value.upper()}
        if 'size_type' in model._fields:
            vals['size_type'] = 'letter'
        return model.create(vals)

    def action_import(self):
        self.ensure_one()
        if self.order_id.state != 'draft':
            raise UserError(_('Chỉ nhập được vào đơn hàng Nháp.'))
        lines = [l for l in self.matrix_text.splitlines() if l.strip()]
        if len(lines) < 2:
            raise UserError(_(
                'Bảng phải có ít nhất 1 dòng size và 1 dòng màu.'))
        Color = self.env['garment.color']
        Size = self.env['garment.size']
        header = self._split(lines[0])
        # Ô đầu của dòng header có thể trống hoặc là nhãn
        sizes = [self._resolve(Size, cell)
                 for cell in header[1:] if cell]
        if not sizes:
            raise UserError(_('Dòng đầu phải chứa danh sách size.'))
        vals_list = []
        for raw in lines[1:]:
            cells = self._split(raw)
            if not cells[0]:
                continue
            color = self._resolve(Color, cells[0])
            for idx, size in enumerate(sizes, start=1):
                if idx >= len(cells) or not cells[idx]:
                    continue
                try:
                    qty = int(float(cells[idx].replace(',', '')))
                except ValueError:
                    raise UserError(_(
                        'Ô "%s" (màu %s / size %s) không phải là số.',
                        cells[idx], color.name, size.name))
                if qty:
                    vals_list.append({
                        'order_id': self.order_id.id,
                        'color_id': color.id,
                        'size_id': size.id,
                        'quantity': qty,
                    })
        if not vals_list:
            raise UserError(_('Không có ô số lượng nào > 0 để nhập.'))
        self.env['garment.order.line'].create(vals_list)
        return {'type': 'ir.actions.act_window_close'}
