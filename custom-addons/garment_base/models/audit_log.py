from odoo import models, fields, api, _
from odoo.http import request as http_request
import json


class GarmentAuditLog(models.Model):
    _name = 'garment.audit.log'
    _description = 'Nhật Ký Kiểm Soát'
    _order = 'create_date desc, id desc'
    _rec_name = 'display_name'

    user_id = fields.Many2one(
        'res.users',
        string='Người Thực Hiện',
        required=True,
        readonly=True,
        index=True,
    )
    action = fields.Selection([
        ('create', 'Tạo Mới'),
        ('write', 'Sửa'),
        ('unlink', 'Xóa'),
        ('state_change', 'Đổi Trạng Thái'),
    ], string='Hành Động', required=True, readonly=True, index=True)

    model_name = fields.Char(
        string='Model',
        required=True,
        readonly=True,
        index=True,
    )
    model_description = fields.Char(
        string='Đối Tượng',
        readonly=True,
    )
    res_id = fields.Integer(
        string='ID Bản Ghi',
        readonly=True,
        index=True,
    )
    record_name = fields.Char(
        string='Tên Bản Ghi',
        readonly=True,
    )
    field_changes = fields.Text(
        string='Chi Tiết Thay Đổi',
        readonly=True,
    )
    old_values = fields.Text(
        string='Giá Trị Cũ (JSON)',
        readonly=True,
    )
    new_values = fields.Text(
        string='Giá Trị Mới (JSON)',
        readonly=True,
    )
    old_state = fields.Char(
        string='Trạng Thái Cũ',
        readonly=True,
    )
    new_state = fields.Char(
        string='Trạng Thái Mới',
        readonly=True,
    )
    ip_address = fields.Char(
        string='Địa Chỉ IP',
        readonly=True,
    )
    note = fields.Text(
        string='Ghi Chú',
        readonly=True,
    )
    severity = fields.Selection([
        ('info', 'Thông Tin'),
        ('warning', 'Cảnh Báo'),
        ('critical', 'Nghiêm Trọng'),
    ], string='Mức Độ', default='info', readonly=True, index=True)

    display_name = fields.Char(
        compute='_compute_display_name',
    )

    def _compute_display_name(self):
        action_labels = dict(
            self._fields['action']._description_selection(self.env)
        )
        for rec in self:
            rec.display_name = '%s — %s — %s' % (
                rec.record_name or rec.model_description or rec.model_name,
                action_labels.get(rec.action, rec.action),
                rec.user_id.name or '',
            )

    @api.model
    def log(self, action, model_name, res_id=0, record_name='',
            field_changes='', old_values=None, new_values=None,
            old_state='', new_state='', note='', severity='info'):
        """Create an audit log entry."""
        model_desc = ''
        try:
            model_obj = self.env.get(model_name)
            if model_obj is not None:
                model_desc = model_obj._description or model_name
        except Exception:
            model_desc = model_name

        ip = ''
        try:
            if http_request and hasattr(http_request, 'httprequest'):
                ip = http_request.httprequest.remote_addr or ''
        except Exception:
            pass

        vals = {
            'user_id': self.env.uid,
            'action': action,
            'model_name': model_name,
            'model_description': model_desc,
            'res_id': res_id,
            'record_name': record_name,
            'field_changes': field_changes,
            'old_values': json.dumps(
                old_values, ensure_ascii=False, default=str
            ) if old_values else False,
            'new_values': json.dumps(
                new_values, ensure_ascii=False, default=str
            ) if new_values else False,
            'old_state': old_state,
            'new_state': new_state,
            'ip_address': ip,
            'note': note,
            'severity': severity,
        }
        return self.sudo().create(vals)


class GarmentAuditMixin(models.AbstractModel):
    """Mixin to add automatic audit logging to critical models.

    Inherit this mixin in models that need deep audit tracking.
    Override _audit_tracked_fields to specify which fields to track.
    """
    _name = 'garment.audit.mixin'
    _description = 'Audit Log Mixin'

    def _audit_tracked_fields(self):
        """Return list of field names to audit. Override in subclass."""
        return []

    def _audit_get_severity(self, action, vals=None):
        """Determine severity based on action type."""
        if action == 'unlink':
            return 'critical'
        if action == 'state_change':
            new_state = (vals or {}).get('state', '')
            if new_state in ('cancelled', 'paid', 'validated'):
                return 'warning'
        return 'info'

    def _audit_format_value(self, field_name, value):
        """Format a field value for display in audit log."""
        if value is False or value is None:
            return ''
        field = self._fields.get(field_name)
        if not field:
            return str(value)
        if field.type == 'many2one':
            if isinstance(value, int):
                try:
                    rec = self.env[field.comodel_name].browse(value)
                    return rec.display_name or str(value)
                except Exception:
                    return str(value)
            elif isinstance(value, models.BaseModel):
                return value.display_name or str(value.id)
            return str(value)
        if field.type == 'selection':
            selection = dict(
                field._description_selection(self.env)
            )
            return selection.get(value, str(value))
        if field.type == 'date':
            return str(value) if value else ''
        if field.type == 'datetime':
            return str(value) if value else ''
        return str(value)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        audit_fields = self._audit_tracked_fields()
        if not audit_fields:
            return records

        AuditLog = self.env['garment.audit.log']
        for record in records:
            new_vals = {}
            changes = []
            for fname in audit_fields:
                val = record[fname]
                formatted = record._audit_format_value(fname, val)
                if formatted:
                    field_str = self._fields[fname].string or fname
                    new_vals[fname] = formatted
                    changes.append('%s: %s' % (field_str, formatted))

            AuditLog.log(
                action='create',
                model_name=self._name,
                res_id=record.id,
                record_name=record.display_name or '',
                field_changes='\n'.join(changes) if changes else '',
                new_values=new_vals or None,
                severity='info',
            )
        return records

    def write(self, vals):
        audit_fields = self._audit_tracked_fields()
        relevant_fields = (
            [f for f in audit_fields if f in vals] if audit_fields else []
        )

        # Capture old values before write
        old_data = {}
        if relevant_fields:
            for record in self:
                old_data[record.id] = {
                    fname: record._audit_format_value(fname, record[fname])
                    for fname in relevant_fields
                }

        result = super().write(vals)

        if relevant_fields:
            AuditLog = self.env['garment.audit.log']
            is_state_change = 'state' in vals

            for record in self:
                old_vals = old_data.get(record.id, {})
                new_vals = {}
                changes = []
                for fname in relevant_fields:
                    new_formatted = record._audit_format_value(
                        fname, record[fname]
                    )
                    old_formatted = old_vals.get(fname, '')
                    if old_formatted != new_formatted:
                        field_str = self._fields[fname].string or fname
                        new_vals[fname] = new_formatted
                        changes.append(
                            '%s: %s → %s' % (
                                field_str, old_formatted, new_formatted
                            )
                        )

                if changes:
                    action = (
                        'state_change' if is_state_change else 'write'
                    )
                    severity = record._audit_get_severity(action, vals)

                    AuditLog.log(
                        action=action,
                        model_name=self._name,
                        res_id=record.id,
                        record_name=record.display_name or '',
                        field_changes='\n'.join(changes),
                        old_values=old_vals or None,
                        new_values=new_vals or None,
                        old_state=(
                            old_vals.get('state', '')
                            if is_state_change else ''
                        ),
                        new_state=(
                            new_vals.get('state', '')
                            if is_state_change else ''
                        ),
                        severity=severity,
                    )
        return result

    def unlink(self):
        audit_fields = self._audit_tracked_fields()
        AuditLog = self.env['garment.audit.log']

        for record in self:
            old_vals = {}
            changes = []
            if audit_fields:
                for fname in audit_fields:
                    formatted = record._audit_format_value(
                        fname, record[fname]
                    )
                    if formatted:
                        field_str = self._fields[fname].string or fname
                        old_vals[fname] = formatted
                        changes.append(
                            '%s: %s' % (field_str, formatted)
                        )

            AuditLog.log(
                action='unlink',
                model_name=self._name,
                res_id=record.id,
                record_name=record.display_name or '',
                field_changes='\n'.join(changes) if changes else '',
                old_values=old_vals or None,
                severity='critical',
                note=_('Bản ghi đã bị xóa vĩnh viễn'),
            )

        return super().unlink()
