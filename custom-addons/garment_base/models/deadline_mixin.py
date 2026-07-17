from odoo import api, fields, models


class GarmentDeadlineMixin(models.AbstractModel):
    """Mixin theo dõi trễ hạn theo một trường ngày hạn chót.

    Model kế thừa cần có trường ``state`` và khai báo:
    - ``_deadline_field``: tên trường Date dùng làm hạn chót
    - ``_deadline_done_states``: các trạng thái kết thúc (không tính trễ)
    """
    _name = 'garment.deadline.mixin'
    _description = 'Mixin Theo Dõi Trễ Hạn'

    _deadline_field = 'deadline'
    _deadline_done_states = ('done', 'cancelled')

    is_overdue = fields.Boolean(
        string='Trễ Hạn',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )
    overdue_days = fields.Integer(
        string='Số Ngày Trễ',
        compute='_compute_is_overdue',
    )

    @api.depends(lambda self: [self._deadline_field, 'state'])
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            deadline = rec[self._deadline_field]
            if deadline and rec.state not in self._deadline_done_states:
                delta = (today - deadline).days
                rec.is_overdue = delta > 0
                rec.overdue_days = max(delta, 0)
            else:
                rec.is_overdue = False
                rec.overdue_days = 0

    def _search_is_overdue(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                (self._deadline_field, '<', today),
                ('state', 'not in', list(self._deadline_done_states)),
            ]
        return [
            '|', '|',
            (self._deadline_field, '=', False),
            (self._deadline_field, '>=', today),
            ('state', 'in', list(self._deadline_done_states)),
        ]
