# PoolMeta and Database Behavior in Tryton / GNUHealth

## No New Table is Created

When a module extends an existing model using `PoolMeta`, Tryton does **not** create a new database table.

```python
class PatientPrescriptionOrder(metaclass=PoolMeta):
    __name__ = 'gnuhealth.prescription.order'
    audit_state = fields.Selection([...], 'Audit Status')
```

This class does **not** inherit from `ModelSQL`, so Tryton never issues a `CREATE TABLE` for it. The target table (`gnuhealth_prescription_order`) already exists and is owned by the original GNUHealth module.

---

## New Fields = New Columns on the Existing Table

Every `fields.*` declaration in a `PoolMeta` class becomes a new column on the target model's existing table, added via `ALTER TABLE` when you run:

```bash
trytond-admin -d <database> -u <module_name>
```

### This module's fields and their resulting columns

| Python field | Column added to `gnuhealth_prescription_order` | PostgreSQL type |
|---|---|---|
| `audit_state` | `audit_state` | `VARCHAR` |
| `audit_notes` | `audit_notes` | `TEXT` |
| `audit_date` | `audit_date` | `TIMESTAMP` |
| `audit_user` | `audit_user` | `INTEGER` (FK → `res_user.id`) |

---

## How the Model Merge Works (MRO)

Tryton's `Pool` collects every class registered under the same `__name__` string across all installed modules. At server startup it merges them into a single class using Python's Method Resolution Order (MRO):

```
Pool["gnuhealth.prescription.order"]
    └── GNUHealth original class  (owns the table)
            + PatientPrescriptionOrder  (this module, merged in)
```

The result is a single unified class. Your fields, methods, and button definitions are indistinguishable from the originals at runtime — same table, same model name, no duplication.

---

## Accessing Other Models Inside a PoolMeta Class

Because `PoolMeta` classes are merged at runtime, you cannot reference sibling models at import time. Always use `Pool()` inside methods:

```python
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

class PatientPrescriptionOrder(metaclass=PoolMeta):
    __name__ = 'gnuhealth.prescription.order'

    @classmethod
    @ModelView.button
    def my_button(cls, records):
        User = Pool().get('res.user')        # correct: resolved at call time
        # User = cls.__pool__.get('res.user') # WRONG: AttributeError
        current_user = User(Transaction().user)
```

`Pool()` is a singleton that is fully populated only after all modules are registered. Calling it inside a method (not at class/module level) guarantees it is ready.

---

## Summary

| Question | Answer |
|---|---|
| Does this module create a new table? | No |
| Does it modify an existing table? | Yes — adds columns via `ALTER TABLE` |
| Which table? | `gnuhealth_prescription_order` |
| When are columns added? | On `trytond-admin -u <module>` |
| Can columns be removed by uninstalling? | No — Tryton never drops columns automatically |
