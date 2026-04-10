# Health Prescription Audit Module - Quick Start Guide

## Module Structure

```
health_prescription_audit/
├── __init__.py                          # Module initialization
├── health_prescription_audit.py         # Main module logic
├── health_prescription_audit_view.xml   # UI/Form definitions
├── tryton.cfg                           # Tryton configuration
├── setup.py                             # Installation setup
├── README.rst                           # Documentation
├── COPYING                              # License
├── MANIFEST.in                          # Package manifest
├── locale/                              # Translations
└── tests/                               # Unit tests
    └── __init__.py
```

## Features Added

### New Fields to gnuhealth.prescription.order

1. **audit_state** (Selection field)
   - Pending Audit (default)
   - Aprobada (Approved)
   - Rechazada (Rejected)

2. **audit_date** (DateTime field)
   - Auto-populated when approve/reject buttons are clicked

3. **audit_user** (Many2One to res.user)
   - Auto-populated with the current user when approve/reject buttons are clicked

4. **audit_notes** (Text field)
   - Editable only when audit_state is 'pending'
   - Allows staff to record reasons for approval/rejection

### New Buttons

1. **Approve** - Sets audit_state to 'aprobada'
2. **Reject** - Sets audit_state to 'rechazada'
3. **Reset Audit** - Returns audit_state to 'pending' (allows re-auditing)

All buttons are only visible when audit_state = 'pending'

## Installation Steps

1. Copy the `health_prescription_audit` folder to your Tryton modules directory
2. Restart Tryton server
3. Go to Modules > Modules, update module list
4. Find and install `health_prescription_audit`
5. Update database

## Usage

1. Open any prescription order
2. Scroll to the "Auditing" section at the bottom
3. Add audit notes in the "Audit Notes" field if needed
4. Click one of the audit action buttons:
   - **Approve** - Mark as aprobada
   - **Reject** - Mark as rechazada
   - **Reset Audit** - Return to pending (if you need to re-audit)

The system automatically records:
- Who performed the audit (audit_user)
- When the audit happened (audit_date)
- The audit decision (audit_state)

## Key Code Components

### Button Decorators in health_prescription_audit.py

```python
@classmethod
@ModelView.button
def approve_prescription(cls, prescriptions):
    # Sets audit_state to 'aprobada'
    # Records current user and timestamp
    
@classmethod
@ModelView.button
def reject_prescription(cls, prescriptions):
    # Sets audit_state to 'rechazada'
    # Records current user and timestamp

@classmethod
@ModelView.button
def reset_audit(cls, prescriptions):
    # Returns to 'pending' state
    # Clears audit_date and audit_user
```

### View XML in health_prescription_audit_view.xml

The module extends the prescription form with:
- An audit status group showing current audit info
- An audit actions group with the three buttons
- An audit notes text field

## Extending Further

To add more audit states or functionality:

1. Modify the state selection in `health_prescription_audit.py`:
   ```python
   audit_state = fields.Selection([
       ('pending', 'Pending Audit'),
       ('aprobada', 'Aprobada'),
       ('rechazada', 'Rechazada'),
       ('revisar', 'Needs Review'),  # Add new state
   ], 'Audit Status', ...)
   ```

2. Add corresponding buttons and methods

3. Update the view XML in `health_prescription_audit_view.xml`

## Dependencies

- gnuhealth (GNU Health core)
- trytond (Tryton framework)
- health module (prescription.order model)

## Notes

- The module uses `PoolMeta` to safely extend the existing `PatientPrescriptionOrder` model
- All audit actions are logged for audit trail purposes
- The module respects Tryton's access control system
