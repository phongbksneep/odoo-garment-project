# Security, Data-Integrity & Performance Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the audit findings across the 27 `garment_*` modules: enforce the 4-level permission scheme, guard all state machines and deletions, remove N+1 queries, add DB indexes, and use precision-safe float comparisons.

**Architecture:** Pure Odoo-layer changes — ACL CSVs + `ir.rule` XML for security, guard helpers in existing `action_*` methods, `_read_group` batching for computes, `index=True` on hot columns. No schema-breaking migrations; every change is upgrade-safe (`-u module`).

**Tech Stack:** Odoo 19 CE in Docker (`garment_odoo` container, DB `garment_db`), Python, XML, CSV.

## Global Constraints

- Group hierarchy (implied chain): `group_garment_user` ⊂ `group_garment_team_leader` ⊂ `group_garment_dept_manager` ⊂ `group_garment_manager` (all in `garment_base`).
- Test command per module: `docker exec garment_odoo odoo -d garment_db --test-enable --test-tags <module> -u <module> --stop-after-init --no-http` — must end with `0 failed, 0 error(s)`.
- All user-facing strings in Vietnamese, wrapped in `_()`, matching existing style.
- Never grant `base.group_user` any garment-model ACL. Never leave a model ACL-less.
- Commit after each task with conventional-commit VN-style messages matching git log.

## Baseline (Task 0)

- [ ] `docker compose up -d` and wait for healthy: `docker exec garment_odoo curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login` → `200`
- [ ] Run baseline tests for the modules this plan touches (must pass BEFORE changes):
  `docker exec garment_odoo odoo -d garment_db --test-enable --test-tags garment_base,garment_payroll,garment_accounting,garment_material,garment_delivery,garment_hr,garment_label,garment_planning,garment_inventory,garment_costing,garment_print,garment_subcontract,garment_packing,garment_warehouse,garment_washing -u garment_base --stop-after-init --no-http`
- [ ] Create branch: `git checkout -b hardening/audit-fixes`

---

### Task 1: garment_material — remove base.group_user full CRUD

**Files:** Modify `custom-addons/garment_material/security/ir.model.access.csv` (whole file)

Replace the 4 `base.group_user,1,1,1,1` lines with garment-group pairs (user read-only, team leader write, manager full):

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_material_receipt_user,garment.material.receipt.user,model_garment_material_receipt,garment_base.group_garment_user,1,0,0,0
access_material_receipt_tl,garment.material.receipt.tl,model_garment_material_receipt,garment_base.group_garment_team_leader,1,1,1,0
access_material_receipt_manager,garment.material.receipt.manager,model_garment_material_receipt,garment_base.group_garment_manager,1,1,1,1
access_material_receipt_line_user,garment.material.receipt.line.user,model_garment_material_receipt_line,garment_base.group_garment_user,1,0,0,0
access_material_receipt_line_tl,garment.material.receipt.line.tl,model_garment_material_receipt_line,garment_base.group_garment_team_leader,1,1,1,0
access_material_receipt_line_manager,garment.material.receipt.line.manager,model_garment_material_receipt_line,garment_base.group_garment_manager,1,1,1,1
access_material_allocation_user,garment.material.allocation.user,model_garment_material_allocation,garment_base.group_garment_user,1,0,0,0
access_material_allocation_tl,garment.material.allocation.tl,model_garment_material_allocation,garment_base.group_garment_team_leader,1,1,1,0
access_material_allocation_manager,garment.material.allocation.manager,model_garment_material_allocation,garment_base.group_garment_manager,1,1,1,1
access_material_allocation_line_user,garment.material.allocation.line.user,model_garment_material_allocation_line,garment_base.group_garment_user,1,0,0,0
access_material_allocation_line_tl,garment.material.allocation.line.tl,model_garment_material_allocation_line,garment_base.group_garment_team_leader,1,1,1,0
access_material_allocation_line_manager,garment.material.allocation.line.manager,model_garment_material_allocation_line,garment_base.group_garment_manager,1,1,1,1
```

NOTE: keep any other lines already in the file that don't reference `base.group_user` (check first; the audit found only these 4 models). The old XML ids (`access_material_receipt`, …) disappear — Odoo will warn about obsolete records; acceptable, or add them to an uninstall cleanup; simplest is to KEEP the same XML ids for the user-level line (rename `access_material_receipt` → keep id, change group/perms) to avoid orphans. Preferred concrete form: reuse old id for the user line, add `_tl`/`_manager` ids as new.

- [ ] Rewrite CSV as above (reusing old ids for user lines)
- [ ] Upgrade + test: `docker exec garment_odoo odoo -d garment_db --test-enable --test-tags garment_material -u garment_material --stop-after-init --no-http` → 0 failed
- [ ] Commit: `git commit -am "fix(security): garment_material không còn cấp full CRUD cho base.group_user"`

### Task 2: garment_delivery — same treatment

**Files:** Modify `custom-addons/garment_delivery/security/ir.model.access.csv`

Same pattern for `garment.vehicle`, `garment.delivery.order`, `garment.delivery.line`: user line (reuse old id) → `garment_base.group_garment_user,1,0,0,0`; new `_tl` line → `garment_base.group_garment_team_leader,1,1,1,0`; manager line (reuse old id) → `garment_base.group_garment_manager,1,1,1,1` (replacing `base.group_system`).

- [ ] Rewrite CSV
- [ ] Test: `--test-tags garment_delivery -u garment_delivery` → 0 failed
- [ ] Commit: `git commit -am "fix(security): garment_delivery dùng nhóm garment thay vì base.group_user"`

### Task 3: Payroll — protect wages and piece-rate output

**Files:**
- Modify `custom-addons/garment_payroll/security/ir.model.access.csv`
- Create `custom-addons/garment_payroll/security/payroll_security.xml`
- Modify `custom-addons/garment_payroll/__manifest__.py` (add the XML to `data` BEFORE the CSV)
- Test: `custom-addons/garment_payroll/tests/test_payroll_security.py` (new)

Changes:
1. CSV: `access_garment_worker_output_user` → perms `1,0,0,0`; add `access_garment_worker_output_tl,garment.worker.output.tl,model_garment_worker_output,garment_base.group_garment_team_leader,1,1,1,0`.
2. Record rule — workers see only their own wage/bonus records:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Công nhân chỉ xem được phiếu lương của chính mình -->
    <record id="rule_wage_calculation_user_own" model="ir.rule">
        <field name="name">Wage: User Sees Own Only</field>
        <field name="model_id" ref="model_garment_wage_calculation"/>
        <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('garment_base.group_garment_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="False"/>
        <field name="perm_create" eval="False"/>
        <field name="perm_unlink" eval="False"/>
    </record>
    <!-- Tổ trưởng trở lên: xem tất cả (rule mở lại phạm vi) -->
    <record id="rule_wage_calculation_tl_all" model="ir.rule">
        <field name="name">Wage: Team Leader+ Sees All</field>
        <field name="model_id" ref="model_garment_wage_calculation"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('garment_base.group_garment_team_leader'))]"/>
    </record>
    <!-- Tương tự cho thưởng -->
    <record id="rule_bonus_line_user_own" model="ir.rule">
        <field name="name">Bonus Line: User Sees Own Only</field>
        <field name="model_id" ref="model_garment_bonus_line"/>
        <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('garment_base.group_garment_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="False"/>
        <field name="perm_create" eval="False"/>
        <field name="perm_unlink" eval="False"/>
    </record>
    <record id="rule_bonus_line_tl_all" model="ir.rule">
        <field name="name">Bonus Line: Team Leader+ Sees All</field>
        <field name="model_id" ref="model_garment_bonus_line"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('garment_base.group_garment_team_leader'))]"/>
    </record>
</odoo>
```

(Check `garment.bonus`/`garment.bonus.line` field names first — rule assumes `employee_id` on the line model; if the parent `garment.bonus` has no employee_id, only add the line rule.)

3. Test (failing first): create a user in `group_garment_user` linked to employee A, wage records for A and B; assert user sees only A's; assert `AccessError` on writing worker.output.

```python
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestPayrollSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worker_user = cls.env['res.users'].create({
            'name': 'Worker A', 'login': 'worker_a_sec',
            'group_ids': [(6, 0, [cls.env.ref('garment_base.group_garment_user').id])],
        })
        cls.emp_a = cls.env['hr.employee'].create({'name': 'Emp A', 'user_id': cls.worker_user.id})
        cls.emp_b = cls.env['hr.employee'].create({'name': 'Emp B'})
        cls.wage_a = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.emp_a.id, 'month': '01', 'year': 2026})
        cls.wage_b = cls.env['garment.wage.calculation'].create({
            'employee_id': cls.emp_b.id, 'month': '01', 'year': 2026})

    def test_worker_sees_only_own_wage(self):
        wages = self.env['garment.wage.calculation'].with_user(self.worker_user).search([])
        self.assertEqual(wages, self.wage_a)

    def test_worker_cannot_create_output(self):
        with self.assertRaises(AccessError):
            self.env['garment.worker.output'].with_user(self.worker_user).create({
                'employee_id': self.emp_b.id, 'date': '2026-01-05', 'quantity': 999})
```

(Adjust required fields of `garment.worker.output` / `garment.wage.calculation` to their actual definitions when writing the test.)

- [ ] Write failing test → run (`--test-tags garment_payroll -u garment_payroll`) → FAIL (worker currently sees both / can create)
- [ ] Apply CSV + XML + manifest changes
- [ ] Run test → PASS; whole module tests → 0 failed
- [ ] Commit: `git commit -am "fix(security): công nhân chỉ xem lương của mình, không sửa được sản lượng"`

### Task 4: Shop-floor ACL sweep — workers read-only on operational documents

**Files:** Modify `security/ir.model.access.csv` in: garment_production, garment_quality, garment_cutting, garment_packing, garment_inventory, garment_warehouse, garment_subcontract, garment_finishing, garment_planning, garment_washing, garment_label, garment_maintenance, garment_sample, garment_compliance, garment_accounting, garment_costing, garment_crm (every CSV line matching `garment_base.group_garment_user,1,1,1,0`).

Transformation per matching line:
1. Change the user line perms to `1,0,0,0`.
2. Add directly below a team-leader line: same model, id suffix `_tl`, group `garment_base.group_garment_team_leader`, perms `1,1,1,0`.

EXCLUDE: `garment_hr` (attendance/leave are self-service with own-data record rules — leave untouched), `garment_mobile` (approval wizards are the worker-facing flow — inspect and keep worker create where the model is a wizard/TransientModel).

Use a script for determinism (run from repo root, then review `git diff` manually):

```bash
python3 - <<'EOF'
import csv, io, pathlib
mods = "garment_production garment_quality garment_cutting garment_packing garment_inventory garment_warehouse garment_subcontract garment_finishing garment_planning garment_washing garment_label garment_maintenance garment_sample garment_compliance garment_accounting garment_costing garment_crm".split()
for m in mods:
    p = pathlib.Path(f"custom-addons/{m}/security/ir.model.access.csv")
    if not p.exists(): continue
    rows = list(csv.reader(io.StringIO(p.read_text())))
    out = [rows[0]]
    for r in rows[1:]:
        if not r: continue
        if r[3] == 'garment_base.group_garment_user' and r[4:8] == ['1','1','1','0']:
            out.append([r[0], r[1], r[2], r[3], '1','0','0','0'])
            out.append([r[0]+'_tl', r[1]+'.tl', r[2], 'garment_base.group_garment_team_leader', '1','1','1','0'])
        else:
            out.append(r)
    buf = io.StringIO(); csv.writer(buf, lineterminator='\n').writerows(out)
    p.write_text(buf.getvalue())
    print("updated", p)
EOF
```

- [ ] Run script, review `git diff --stat` and spot-check 3 files
- [ ] Upgrade all touched modules + run their tests (single command with combined `--test-tags`) → 0 failed
- [ ] Commit: `git commit -am "fix(security): công nhân chỉ đọc chứng từ vận hành, tổ trưởng trở lên mới được ghi"`

### Task 5: HR PII field groups

**Files:** Modify `custom-addons/garment_hr/models/garment_employee.py:44-49`

Add `groups='hr.group_hr_user'` to `id_number`, `insurance_number`, `tax_code`, `bank_name`, `bank_account`. First grep views/reports for these field names (`grep -rn "bank_account\|tax_code\|insurance_number\|id_number" custom-addons/*/views custom-addons/*/report`) — if a QWeb report used by non-HR users prints them, wrap with `t-if` on group or leave that field out.

- [ ] Grep usages, adjust plan if a report prints them
- [ ] Add `groups=` to the 5 fields
- [ ] Test: `--test-tags garment_hr -u garment_hr` → 0 failed
- [ ] Commit: `git commit -am "fix(security): giới hạn trường PII nhân viên cho nhóm HR"`

---

### Task 6: garment.order state-machine guards + unlink protection

**Files:**
- Modify `custom-addons/garment_base/models/garment_order.py:206-234`
- Test: `custom-addons/garment_base/tests/test_order_workflow_guards.py` (new)

Implementation (replace the bare `action_*` bodies):

```python
    # Thứ tự pipeline; cancel/reset xử lý riêng
    _STATE_FLOW = ['draft', 'confirmed', 'material', 'cutting', 'sewing',
                   'finishing', 'qc', 'packing', 'shipped', 'done']

    def _check_forward(self, new_state):
        """Chỉ cho phép đi tới (không lùi), không rời trạng thái kết thúc."""
        flow = self._STATE_FLOW
        for order in self:
            if order.state in ('done', 'cancelled'):
                raise UserError(_(
                    'Đơn hàng %s đã kết thúc (%s), không thể chuyển trạng thái.',
                    order.name, order.state))
            if order.state == 'draft' and new_state != 'confirmed':
                raise UserError(_(
                    'Đơn hàng %s phải được xác nhận trước.', order.name))
            if flow.index(new_state) <= flow.index(order.state):
                raise UserError(_(
                    'Không thể chuyển đơn hàng %s từ "%s" lùi về "%s".',
                    order.name, order.state, new_state))
        self.write({'state': new_state})

    def action_material(self):
        self._check_forward('material')

    def action_cutting(self):
        self._check_forward('cutting')

    def action_sewing(self):
        self._check_forward('sewing')

    def action_finishing(self):
        self._check_forward('finishing')

    def action_qc(self):
        self._check_forward('qc')

    def action_packing(self):
        self._check_forward('packing')

    def action_shipped(self):
        self._check_forward('shipped')

    def action_done(self):
        self._check_forward('done')

    def action_cancel(self):
        for order in self:
            if order.state in ('shipped', 'done'):
                raise UserError(_(
                    'Không thể hủy đơn hàng %s đã giao/hoàn thành.', order.name))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for order in self:
            if order.state not in ('confirmed', 'cancelled'):
                raise UserError(_(
                    'Chỉ đơn hàng Đã Xác Nhận hoặc Đã Hủy mới được đưa về Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancelled'):
                raise UserError(_(
                    'Không thể xóa đơn hàng %s ở trạng thái "%s". '
                    'Hãy hủy đơn trước.', order.name, order.state))
        return super().unlink()
```

`action_confirm` additionally gets a state guard at the top of the existing method:

```python
        for order in self:
            if order.state != 'draft':
                raise UserError(_('Chỉ đơn hàng Nháp mới được xác nhận.'))
```

Import `UserError` (file currently imports only `ValidationError`).

Tests (write FIRST, verify they fail):

```python
from odoo.exceptions import UserError
from odoo.tests import TransactionCase

class TestOrderWorkflowGuards(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # build a confirmable order with one line (reuse helpers from existing garment_base tests)
        ...

    def test_draft_cannot_jump_to_done(self):
        with self.assertRaises(UserError):
            self.order.action_done()

    def test_cannot_confirm_twice(self):
        self.order.action_confirm()
        with self.assertRaises(UserError):
            self.order.action_confirm()

    def test_no_backward_transition(self):
        self.order.action_confirm()
        self.order.action_material()
        self.order.action_cutting()
        with self.assertRaises(UserError):
            self.order.action_material()

    def test_done_is_terminal(self):
        ...  # walk to done, then assertRaises on action_cancel / action_reset_draft

    def test_cannot_delete_confirmed(self):
        self.order.action_confirm()
        with self.assertRaises(UserError):
            self.order.unlink()

    def test_delete_draft_ok(self):
        self.order.unlink()
```

CAUTION: existing tests in other modules may drive `garment.order` through states — expect some to call e.g. `action_done()` from draft. Run the FULL suite after this task; fix any test that relied on skipping states by walking the pipeline properly (that is the point of the change).

- [ ] Write failing tests → run → FAIL
- [ ] Implement guards + unlink
- [ ] `--test-tags garment_base -u garment_base` → 0 failed
- [ ] Full suite (all 25 tagged modules) → fix fallout in tests that skipped states
- [ ] Commit: `git commit -am "fix(base): thêm guard máy trạng thái và chặn xóa đơn hàng đã xác nhận"`

### Task 7: garment_invoice guards

**Files:** Modify `custom-addons/garment_accounting/models/garment_invoice.py:213-229`; add tests to `custom-addons/garment_accounting/tests/` (new file `test_invoice_guards.py`).

```python
    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Chỉ hóa đơn Nháp mới được xác nhận.'))
            if not rec.line_ids:
                raise UserError(_('Phải có ít nhất 1 dòng chi tiết!'))
        self.write({'state': 'confirmed'})

    def action_paid(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_('Chỉ hóa đơn Đã Xác Nhận mới được ghi nhận thanh toán.'))
        self.write({'state': 'paid'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_('Không thể hủy hóa đơn đã thanh toán!'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_('Không thể đưa hóa đơn đã thanh toán về Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state in ('confirmed', 'paid'):
                raise UserError(_(
                    'Không thể xóa hóa đơn %s đã xác nhận/thanh toán.', rec.name))
        return super().unlink()
```

Tests: paid→reset raises; paid→pay-again raises (confirm-only); confirmed unlink raises; draft unlink ok.

- [ ] Failing tests → implement → module tests 0 failed → commit `fix(accounting): guard trạng thái hóa đơn, chặn xóa/reset hóa đơn đã thanh toán`

### Task 8: wage_calculation guards

**Files:** Modify `custom-addons/garment_payroll/models/wage_calculation.py:394-406`; tests in `custom-addons/garment_payroll/tests/test_wage_guards.py` (new).

```python
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'calculated':
            raise UserError(_('Phải tính lương trước khi xác nhận.'))
        self.write({'state': 'confirmed'})

    def action_reset_draft(self):
        self.ensure_one()
        if self.state == 'paid':
            raise UserError(_('Không thể đưa phiếu lương đã trả về Nháp.'))
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_('Không thể xóa phiếu lương %s đã trả.', rec.name))
        return super().unlink()
```

Also guard `action_calculate` (top of method): only from `draft`/`calculated`.

- [ ] Failing tests (confirm-from-draft raises; paid reset raises; paid unlink raises) → implement → 0 failed → commit `fix(payroll): guard trạng thái phiếu lương, chặn trả lương hai lần`

### Task 9: qc_inspection guards + NEW test module for garment_quality

**Files:**
- Modify `custom-addons/garment_quality/models/qc_inspection.py:169-176`
- Create `custom-addons/garment_quality/tests/__init__.py`, `custom-addons/garment_quality/tests/test_qc_inspection.py`

```python
    def action_start(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Chỉ phiếu kiểm Nháp mới được bắt đầu.'))
        self.write({'state': 'in_progress'})

    def action_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_('Phiếu kiểm phải Đang Kiểm mới được hoàn thành.'))
        self.write({'state': 'done'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Không thể hủy phiếu kiểm đã hoàn thành.'))
        self.write({'state': 'cancelled'})
```

Add `UserError` import. Test module covers: happy path draft→in_progress→done; guards (done-from-draft raises, cancel-done raises); compute checks (`pass_rate`, `failed_qty`, defect severity sums).

- [ ] Failing tests → implement → `--test-tags garment_quality -u garment_quality` 0 failed → commit `feat(quality): guard trạng thái QC + bộ test đầu tiên cho garment_quality`

### Task 10: Uniform reset/terminal guards in 6 remaining modules

**Files:**
- `custom-addons/garment_delivery/models/delivery_order.py` (:122-145) — `action_reset_draft` raise if state == 'delivered'; `action_confirm` only from draft; forward chain confirmed→loading→in_transit→delivered each requiring its predecessor; unlink blocked unless draft/cancelled.
- `custom-addons/garment_material/models/material_allocation.py` (:91-107) — `action_issue` only from 'confirmed'; `action_reset_draft` raise if 'issued'; unlink blocked if 'issued'.
- `custom-addons/garment_packing/models/packing_list.py` (:161-195) — forward chain draft→packing→packed→shipped→delivered; reset only from packing/cancelled; unlink blocked from shipped/delivered.
- `custom-addons/garment_warehouse/models/stock_move.py` (:109-125) — done requires confirmed; reset blocked from done; unlink blocked from done.
- `custom-addons/garment_subcontract/models/subcontract_order.py` (:225-262) — reset blocked from done/received; unlink blocked from done.
- `custom-addons/garment_label/models/pallet.py` (:97-119) — ship requires closed; reset blocked from shipped; unlink blocked from shipped.

Guard pattern is identical to Tasks 7-9 (per-record loop, `UserError`, VN message). Add 2-4 negative tests per module in the existing tests/ dirs.

- [ ] Implement + tests module by module, running each module's tags → 0 failed
- [ ] Commit per module or one commit: `fix: guard trạng thái và chặn xóa chứng từ đã hoàn tất (delivery, material, packing, warehouse, subcontract, label)`

---

### Task 11: DB indexes on hot columns

**Files:**
- `custom-addons/garment_base/models/garment_order.py` — add `index=True` to `customer_id` (:22), `style_id` (:33), `delivery_date` (:44), `state` (:74)
- `custom-addons/garment_production/models/production_order.py` — `garment_order_id`, `sewing_line_id`
- `custom-addons/garment_payroll/models/worker_output.py` — `employee_id`, `date` (find exact lines)
- `custom-addons/garment_quality/models/qc_inspection.py` — defect line `inspection_id`
- `custom-addons/garment_production/models/daily_output.py` — `production_order_id` (find exact file/lines)

Adding `index=True` to an existing column only issues `CREATE INDEX` on upgrade — safe.

- [ ] Add index=True at each location; `-u garment_base,garment_production,garment_payroll,garment_quality` with tests → 0 failed
- [ ] Verify: `docker exec garment_db psql -U odoo -d garment_db -c "\d garment_order" | grep -i idx` shows new indexes
- [ ] Commit: `perf: thêm index cho các cột lọc/join nóng (state, delivery_date, FK báo cáo)`

### Task 12: Payroll N+1 → batched _read_group

**Files:** Modify `custom-addons/garment_payroll/models/wage_calculation.py:252-280`; test in `tests/test_wage_guards.py` (assert totals correct for 2 employees computed in one batch).

```python
    @api.depends('employee_id', 'month', 'year')
    def _compute_piece_totals(self):
        valid = self.filtered(lambda r: r.employee_id and r.month and r.year)
        for record in self - valid:
            record.total_pieces = 0
            record.piece_rate_amount = 0
            record.total_ot_hours = 0
        if not valid:
            return
        date_from = min(v._period_start() for v in valid)
        date_to = max(v._period_end() for v in valid)
        groups = self.env['garment.worker.output']._read_group(
            domain=[('employee_id', 'in', valid.employee_id.ids),
                    ('date', '>=', date_from), ('date', '<', date_to)],
            groupby=['employee_id', 'date:month'],
            aggregates=['quantity:sum', 'amount:sum', 'overtime_hours:sum'],
        )
        data = {}
        for employee, month_start, qty, amount, ot in groups:
            data[(employee.id, month_start.year, month_start.month)] = (qty, amount, ot)
        for record in valid:
            key = (record.employee_id.id, record.year, int(record.month))
            qty, amount, ot = data.get(key, (0, 0, 0))
            record.total_pieces = qty
            record.piece_rate_amount = amount
            record.total_ot_hours = ot

    def _period_start(self):
        self.ensure_one()
        return fields.Date.to_date(f'{self.year}-{self.month}-01')

    def _period_end(self):
        self.ensure_one()
        if int(self.month) == 12:
            return fields.Date.to_date(f'{self.year + 1}-01-01')
        return fields.Date.to_date(f'{self.year}-{str(int(self.month) + 1).zfill(2)}-01')
```

(Verify `_read_group` tuple ordering & `date:month` granularity return type against Odoo 19 — it returns the month start as `date`; adjust key building accordingly at implementation time.)

- [ ] Add test computing wages for 2 employees, assert totals equal per-employee sums → currently passes (behavior-preserving); refactor; test still passes; module 0 failed
- [ ] Commit: `perf(payroll): gộp truy vấn sản lượng bằng _read_group thay vì search theo từng nhân viên`

### Task 13: Remove per-line search_count constraint (redundant with SQL constraint)

**Files:** `custom-addons/garment_base/models/garment_order.py:276-296`

Verify the `_sql_constraints` UNIQUE(order_id, color_id, size_id) actually exists on the line model; if yes, DELETE the Python `_check_unique_color_size` method (redundant N+1). If the SQL constraint does NOT cover it, replace the Python check with one that validates in-memory within the recordset + a single batched search.

- [ ] Inspect; delete or batch; ensure an existing duplicate-line test still raises (SQL constraint raises `psycopg2.IntegrityError` wrapped as `ValidationError` — update test expectation if needed)
- [ ] `--test-tags garment_base -u garment_base` → 0 failed → commit `perf(base): bỏ kiểm tra trùng màu/size chạy N+1, dựa vào unique constraint DB`

### Task 14: label_count + planning cron batching

**Files:**
- `custom-addons/garment_label/models/delivery_integration.py:30-38`: batch with one `_read_group`:

```python
    @api.depends('garment_order_id')
    def _compute_label_count(self):
        counts = {}
        order_ids = self.garment_order_id.ids
        if order_ids:
            for order, count in self.env['garment.label']._read_group(
                    [('garment_order_id', 'in', order_ids)],
                    ['garment_order_id'], ['__count']):
                counts[order.id] = count
        for rec in self:
            rec.label_count = counts.get(rec.garment_order_id.id, 0)
```

- `custom-addons/garment_planning/models/production_plan.py:209-227`: replace per-plan activity search with one search over all plan ids:

```python
        existing_ids = set(self.env['mail.activity'].search([
            ('res_model_id', '=', model_id),
            ('res_id', 'in', plans.ids),
            ('activity_type_id', '=', activity_type.id),
            ('date_deadline', '=', today),
        ]).mapped('res_id'))
        for plan in plans:
            if plan.id in existing_ids:
                continue
            ...
```

- [ ] Implement both; run garment_label + garment_planning tests → 0 failed
- [ ] Commit: `perf: gộp truy vấn label_count và cron cảnh báo deadline`

---

### Task 15: float_compare / float_is_zero pass

**Files:**
- `custom-addons/garment_inventory/models/inventory.py` (:107, :243 — `l.diff_qty != 0` → `not float_is_zero(l.diff_qty, precision_digits=2)`)
- `custom-addons/garment_washing/models/wash_order.py` (:219 — `qty_washed > qty_received` → `float_compare(qty_washed, qty_received, precision_digits=2) > 0`)
- `custom-addons/garment_subcontract/models/subcontract_order.py` (:328 — same pattern)
- Grep for other `>` / `!=` on qty/amount floats in cutting/packing/costing constraints and convert the constraint-relevant ones only.

Import: `from odoo.tools import float_compare, float_is_zero`.

- [ ] Implement; run garment_inventory, garment_washing, garment_subcontract tests → 0 failed
- [ ] Commit: `fix: so sánh số lượng bằng float_compare/float_is_zero tránh lỗi làm tròn`

---

### Task 16: garment.deadline.mixin (dedupe _compute_is_overdue)

**Files:**
- Create `custom-addons/garment_base/models/deadline_mixin.py`; register in `models/__init__.py`
- Refactor consumers whose semantics match exactly (deadline date + open-states set): `garment_production/models/production_order.py:141`, `garment_maintenance/models/maintenance_request.py:87`, `garment_compliance/models/corrective_action.py:80`, `garment_finishing/models/finishing_order.py:158`, `garment_subcontract/models/subcontract_order.py:204`, `garment_crm/models/crm_feedback.py:130`, `garment_crm/models/crm_lead.py:163`. LEAVE `garment_invoice` (residual-based, different semantics).

```python
from odoo import api, fields, models


class GarmentDeadlineMixin(models.AbstractModel):
    _name = 'garment.deadline.mixin'
    _description = 'Mixin Theo Dõi Trễ Hạn'

    _deadline_field = 'deadline'          # override in consumer
    _deadline_done_states = ('done', 'cancelled')  # override in consumer

    is_overdue = fields.Boolean(
        string='Trễ Hạn', compute='_compute_is_overdue')
    overdue_days = fields.Integer(
        string='Số Ngày Trễ', compute='_compute_is_overdue')

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
```

Consumer pattern: add `'garment.deadline.mixin'` to `_inherit`, set `_deadline_field`/`_deadline_done_states`, DELETE the local `is_overdue`/`overdue_days`(or `delay_days`) fields + compute. CAUTION: some consumers name the day-counter differently (`delay_days`) and views/filters reference it — grep each module's views for the old field names and update, or keep a related field alias. Refactor ONE module first (production), run its tests, then roll to the rest.

- [ ] Mixin + refactor production_order → tests pass
- [ ] Roll out to remaining 6 files, checking each module's views/search filters for renamed fields → each module's tests pass
- [ ] Commit: `refactor: gom logic trễ hạn về garment.deadline.mixin trong garment_base`

### Task 17: Fix garment_costing dependency

**Files:** `custom-addons/garment_costing/__manifest__.py:23`

- [ ] Confirm: `grep -rn "garment.production\|garment_production" custom-addons/garment_costing --include="*.py" --include="*.xml"` returns nothing runtime-relevant
- [ ] Change `'depends': ['garment_production']` → `'depends': ['garment_base']` (keep other deps)
- [ ] `--test-tags garment_costing -u garment_costing` → 0 failed → commit `fix(costing): bỏ dependency thừa vào garment_production`

### Task 18: t-esc → t-out in print reports

**Files:** `custom-addons/garment_print/report/report_invoice.xml`, `report_packing_list.xml`, `report_payslip.xml`, `report_qc_inspection.xml`, `report_delivery_order.xml`

- [ ] `sed -i '' 's/t-esc=/t-out=/g' custom-addons/garment_print/report/*.xml` then `git diff` review
- [ ] `-u garment_print` + tests → 0 failed; render one PDF smoke-test via existing print tests
- [ ] Commit: `fix(print): thay t-esc deprecated bằng t-out trong 5 báo cáo QWeb`

### Task 19: Unique constraints on document numbers

**Files:** Add SQL unique constraints (follow the existing `_sql_constraints` style in garment_order.py) on `name` for: `garment.order`, `garment.invoice`, `garment.wage.calculation`, `garment.qc.inspection`.

```python
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Số chứng từ phải là duy nhất!'),
    ]
```

- [ ] Check for existing duplicates first: `docker exec garment_db psql -U odoo -d garment_db -c "SELECT name, COUNT(*) FROM garment_order GROUP BY name HAVING COUNT(*)>1"` (repeat per table); dedupe demo data if any
- [ ] Add constraints; upgrade 4 modules + tests → 0 failed
- [ ] Commit: `fix: unique constraint cho số chứng từ (đơn hàng, hóa đơn, phiếu lương, phiếu QC)`

### Task 20: ondelete='restrict' on master-data references

**Files:** `custom-addons/garment_base/models/garment_order.py` — `customer_id`, `style_id` get `ondelete='restrict'`.

- [ ] Add; `-u garment_base` + tests → 0 failed
- [ ] Commit: `fix(base): ondelete=restrict cho khách hàng/mẫu may trên đơn hàng`

### Task 21: Final full-suite verification + docs

- [ ] Run FULL suite (all 25 module tags, command from README:182) → 0 failed
- [ ] Update README test counts if changed; note the security model change (workers read-only on operational docs) in README's permission section
- [ ] Final commit + summary of all changes

## Deferred (explicitly out of scope, with reasons)

- Consolidating the duplicated `state` Selection across ~32 models — high churn, zero functional gain, risks breaking views/translations; do opportunistically later.
- Merging `garment.cutting.order` and `garment.cutting.order.adv` — product decision about which is authoritative; needs the user.
- Multi-company `company_id` record rules — single-company deployment today.
- Dashboard materialized view — indexes from Task 11 first; revisit if still slow with real data volume.
- Docker/odoo.conf production hardening (passwords, exposed 5432, proxy_mode) — deployment-time change, needs user's infra decisions.
- Attendance `action_calculate` batching (perf #7) — only slow on rare bulk recalcs.
