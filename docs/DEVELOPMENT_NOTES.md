# GNUHealth 4.2 Custom Module Development Notes

## Module Structure

A GNUHealth 4.2 custom module requires the following files:

```
module_name/
├── __init__.py
├── tryton.cfg
├── module_name.py
├── module_name_view.xml
└── view/
    └── some_form.xml
```

### tryton.cfg

```ini
[tryton]
version=4.2.0        # Must match GNUHealth version (first two digits)
depends:
    ir               # Always required
    health           # Plus any other module dependencies
xml:
    module_name_view.xml
```

- `version` first two digits must match the target GNUHealth version
- `ir` must always be listed in `depends`
- Only list XML data files here — view arch files in `view/` are loaded automatically via the `name` field on `ir.ui.view` records

### __init__.py

```python
from trytond.pool import Pool
from . import module_name

def register():
    Pool.register(
        module_name.MyModel,
        module='module_name', type_='model')
```

Register classes by type: `model`, `wizard`, `report`.

---

## Extending an Existing Model (PoolMeta)

Use `PoolMeta` to extend an existing GNUHealth model without replacing it:

```python
from trytond.pool import PoolMeta

class Appointment(metaclass=PoolMeta):
    'Appointment extension'
    __name__ = 'gnuhealth.appointment'   # Must match the target model's __name__

    new_field = fields.Char('New Field')
```

This is the correct pattern for custom modules that add fields or behaviour to
existing GNUHealth models.

---

## Extending an Existing View (Inherited Views)

### Data XML (module_name_view.xml)

Declare the view record with `inherit` and `name` — no inline arch:

```xml
<record model="ir.ui.view" id="my_extension_form">
    <field name="model">gnuhealth.appointment</field>
    <field name="inherit" ref="health.gnuhealth_appointment_form"/>
    <field name="name">my_extension_form</field>
</record>
```

- `inherit`: points to the parent view's XML id using `module.view_id` format
- `name`: filename (without `.xml`) of the arch file inside `view/`
- Do **not** put the arch XML inline here

### Arch File (view/my_extension_form.xml)

```xml
<?xml version="1.0"?>
<data>
    <xpath expr="/form/field[@name='some_field']" position="after">
        <label name="new_field"/>
        <field name="new_field"/>
    </xpath>
</data>
```

- Root element is `<data>`, not `<form>`
- Use `<xpath>` with `expr=` (path to target element) and `position=` (`after`, `before`, `replace`)
- Single quotes inside `expr` are fine in a standalone XML file; use `&quot;` only when arch is embedded inside another XML document

---

## Buttons

Buttons require two things: registration in `_buttons` and the method decorator.

### In __setup__ (Python)

```python
@classmethod
def __setup__(cls):
    super().__setup__()
    cls._buttons.update({
        'my_button': {
            'invisible': Eval('state') != 'draft',
            'depends': ['state'],
        },
    })
```

Every method decorated with `@ModelView.button` **must** have a corresponding
entry in `_buttons`. Missing this causes a runtime access-denied error when the
button is clicked.

### Method

```python
@classmethod
@ModelView.button
def my_button(cls, records):
    cls.write(records, {'state': 'done'})
```

### In the view arch

```xml
<button name="my_button"
        string="Do It"
        icon="tryton-ok"
        help="Tooltip text"/>
```

---

## Form View Element Rules

### separator

Always requires an `id` attribute — omitting it fails RelaxNG validation:

```xml
<!-- Correct -->
<separator string="Section Title" colspan="4" id="separator_section_title"/>

<!-- Wrong — missing id -->
<separator string="Section Title" colspan="4"/>
```

### group

```xml
<group string="Group Label" id="group_id" colspan="4" col="4">
    ...
</group>
```

- `col` sets the number of columns inside the group (default 4)
- `colspan` sets how many columns the group itself occupies in its parent

### field / label

```xml
<label name="field_name"/>
<field name="field_name" colspan="2"/>
```

Labels and fields are separate elements in Tryton forms.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `Tags 'form' not supported inside tag record` | Inline arch wrapped in `<form>` inside data XML | Move arch to `view/` file; use `<data>` as root |
| `Reference to health.some_view not found` | Wrong `ref` id in `inherit` field | Check the target module's XML for the correct `id=` value |
| `Element separator failed to validate attributes` | `<separator>` missing `id` attribute | Add `id="separator_unique_name"` |
| Button raises access error at runtime | Button method not in `_buttons` | Add entry to `cls._buttons.update({...})` in `__setup__` |
| `File not found: tryton.cfg` | Module folder not in Tryton's modules path | Copy/symlink folder to `trytond/modules/` |

---

## Finding the Correct View ID for inherit ref

The `ref` value in `<field name="inherit" ref="module.view_id"/>` must match
an `id=` attribute in the target module's data XML.

To find it, search the target module's XML files:

```bash
grep -r 'id="' /path/to/gnuhealth/modules/health/*.xml | grep prescription
```

For GNUHealth 4.2, the prescription order form view is:
`ref="health.gnuhealth_prescription_view"`

---

## Useful GNUHealth Model Names

| Model | __name__ |
|---|---|
| Patient | `gnuhealth.patient` |
| Appointment | `gnuhealth.appointment` |
| Prescription | `gnuhealth.prescription.order` |
| Health Professional | `gnuhealth.healthprofessional` |
