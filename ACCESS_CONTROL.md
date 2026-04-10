# Access Control in health_prescription_audit

## Current State

The module currently defines **no access control**. Only a view record exists in the XML.
This means:

- Any user who can edit a prescription can also write `audit_state`, `audit_notes`, `audit_date`, and `audit_user` directly.
- Any logged-in user can trigger `approve_prescription`, `reject_prescription`, or `reset_audit` via RPC, regardless of the button being hidden in the UI.

---

## The Three Layers of Access Control in Tryton

### Layer 1 — Model Access (`ir.model.access`)

Controls read/write/create/delete at the **entire model** level. The new fields inherit whatever rules already exist for `gnuhealth.prescription.order` from the base `health` module. You do not need to redefine model access unless you want to restrict it further than the base module does.

### Layer 2 — Field Access (`ir.model.field.access`)

Controls read/write per **individual field** per **group**. Without this, all fields are accessible to anyone who passes Layer 1.

```xml
<record model="ir.model.field.access" id="access_audit_state_auditor_write">
    <field name="field" search="[
        ('model.model', '=', 'gnuhealth.prescription.order'),
        ('name', '=', 'audit_state')]"/>
    <field name="group" ref="group_prescription_auditor"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
</record>
```

Must be repeated for each field (`audit_state`, `audit_notes`, `audit_date`, `audit_user`) and each group that needs access.

### Layer 3 — Button Rules (`ir.model.button` + `ir.model.button.rule`)

**PYSON `invisible` conditions are client-side UI only — they are not a security control.**
The server will execute the method regardless of whether the button was visible.

To enforce server-side button access:

**Step 1** — Register the button as a protected resource:
```xml
<record model="ir.model.button" id="button_approve_prescription">
    <field name="name">approve_prescription</field>
    <field name="model" search="[('model', '=', 'gnuhealth.prescription.order')]"/>
</record>
```

**Step 2** — Tie it to a group:
```xml
<record model="ir.model.button.rule" id="rule_approve_prescription">
    <field name="button" ref="button_approve_prescription"/>
    <field name="group" ref="group_prescription_auditor"/>
</record>
```

Without Step 2, the button method is callable by any authenticated user via RPC.

---

## What Needs to Be Implemented

### 1. Define a custom group

```xml
<record model="res.group" id="group_prescription_auditor">
    <field name="name">Prescription Auditor</field>
</record>
```

### 2. Restrict the audit fields (Layer 2)

One record per field, per group. Fields that should only be written by auditors:

| Field | Auditors can write | Regular users can read |
|---|---|---|
| `audit_state` | Yes | Yes (to see status) |
| `audit_notes` | Yes | Yes (to see decision notes) |
| `audit_date` | Yes (auto-set by button) | Yes |
| `audit_user` | Yes (auto-set by button) | Yes |

### 3. Protect the buttons (Layer 3)

Must declare `ir.model.button` + `ir.model.button.rule` for each of the three buttons:

| Button | Who should be allowed |
|---|---|
| `approve_prescription` | `group_prescription_auditor` |
| `reject_prescription` | `group_prescription_auditor` |
| `reset_audit` | `group_prescription_auditor` (or admin only) |

---

## View-Level Hiding (`groups` attribute)

The `groups` attribute on view arch elements hides UI elements for users who do not belong to the specified group. It is set directly in the arch XML file and requires no Python changes.

```xml
<group id="group_audit_status"
       groups="health_prescription_audit.group_prescription_auditor">
    ...
</group>
```

The format is `module_name.xml_id_of_group`. In Tryton 6.0, `groups=` is **not supported on `<group>` container elements** — it must be applied individually to each `<field>`, `<button>`, and `<separator>` inside.

> **Deployment note:** `module_name` here must be the name the module is actually registered under in the database — i.e. the folder name in `trytond/modules/` and the `module=` value in `Pool.register()`. If the module is deployed as `test_module`, the reference must be `test_module.group_prescription_auditor`, not `health_prescription_audit.group_prescription_auditor`. A wrong module prefix causes the groups filter to silently fail — the element becomes visible to everyone.

### What is hidden from non-auditors in this module

All three audit sections are hidden entirely:

| Element | groups= applied on |
|---|---|
| Status section (state, date, user) | `<group id="group_audit_status">` |
| Action buttons (approve, reject, reset) | `<group id="group_audit_action">` |
| Audit notes field | `<field name="audit_notes">` |

Non-auditors open the prescription form and see no trace of the audit section.

---

## Important Distinction: Visibility vs. Security

| Mechanism | Where enforced | Can be bypassed? |
|---|---|---|
| `groups=` on view element | Client (browser/GTK) | Yes — direct RPC call |
| PYSON `invisible` on button | Client (browser/GTK) | Yes — direct RPC call |
| `ir.model.button.rule` | Server | No |
| `ir.model.field.access` | Server | No |
| `ir.model.access` | Server | No |

Never rely on `groups=` or PYSON conditions alone to protect sensitive operations. They must always be backed by server-side rules.

---

## How It Works Once Implemented

### Step 1 — XML records are added and the module is updated

After adding the `res.group`, `ir.model.field.access`, `ir.model.button`, and `ir.model.button.rule` records to the XML, run:

```bash
trytond-admin -d health -u health_prescription_audit
```

Tryton reads the XML and inserts those records into the corresponding database tables. The server enforces them on every request from that point on.

### Step 2 — The group exists but has no users yet

The `Prescription Auditor` group now exists in the DB but is empty. **No behavior changes for anyone yet** — all users still behave as before because the group has no members.

### Step 3 — An administrator assigns users to the group

In the GNUHealth / Tryton client:

```
Administration → Users → (select user) → Groups tab → add "Prescription Auditor"
```

From that moment, that user gains the field write access and button execution rights defined for the group.

### Step 4 — What each user experiences

**User WITHOUT the auditor group:**
- Can open a prescription and read `audit_state`, `audit_notes`, `audit_date`, `audit_user`
- Approve/reject/reset buttons are hidden by PYSON (already the case)
- If they call a button via RPC anyway → server returns **Access Denied**
- If they try to write an audit field directly via RPC → server returns **Access Denied**

**User WITH the auditor group:**
- Sees the approve/reject/reset buttons when `audit_state == 'pending'`
- Can click them → server validates group membership → method executes
- Can write audit fields directly if needed

---

## Server-Side Check Flow (what happens on every button click)

```
User clicks "Approve" button
        │
        ▼
RPC call arrives at trytond dispatcher
        │
        ▼
trytond checks ir.model.button.rule for 'approve_prescription'
        │
        ├── user's groups ∩ allowed groups = empty → AccessError, method never runs
        │
        └── user's groups ∩ allowed groups = match → method executes
                │
                ▼
        cls.write(...) called
                │
                ▼
        trytond checks ir.model.field.access for each field being written
                │
                ├── group not allowed to write audit_state → AccessError
                │
                └── group allowed → write committed to DB
```

### What does NOT change

- PYSON `invisible` conditions still control UI visibility independently — both mechanisms work together: the button is hidden AND blocked server-side.
- Model-level access for `gnuhealth.prescription.order` is untouched — users can still create, read, and write prescriptions normally.
- `audit_date` and `audit_user` are set automatically inside the button methods, so regular users never need to write them directly. The field access restriction on those two blocks direct RPC writes that bypass the button.

---

## Full Lifecycle Summary

```
XML defined → trytond-admin -u → records inserted in DB
                                        │
                                        ▼
                            Admin assigns users to group
                                        │
                                        ▼
                    Server enforces field access + button rules on every call
                                        │
                            ┌───────────┴───────────┐
                      no group match            group match
                      AccessError            method executes
```

---

## Full Implementation Checklist

- [ ] Define `res.group` record for `Prescription Auditor`
- [ ] Add `ir.model.field.access` records for all 4 audit fields
- [ ] Add `ir.model.button` record for `approve_prescription`
- [ ] Add `ir.model.button.rule` linking it to the auditor group
- [ ] Add `ir.model.button` record for `reject_prescription`
- [ ] Add `ir.model.button.rule` linking it to the auditor group
- [ ] Add `ir.model.button` record for `reset_audit`
- [ ] Add `ir.model.button.rule` linking it to the auditor group
- [ ] Run `trytond-admin -u health_prescription_audit` to apply
- [ ] Assign the `Prescription Auditor` group to the appropriate users in the client
