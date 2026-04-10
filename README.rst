========================================
GNU Health Prescription Auditing Module
========================================

Overview
========

The Health Prescription Auditing module extends the GNU Health prescription system with auditing capabilities. It allows healthcare staff to audit and approve or reject prescriptions through a simple UI interface.

Features
========

- **Audit States**: Track prescription auditing status with three states:
  - Pending Audit
  - Aprobada (Approved)
  - Rechazada (Rejected)

- **Audit Tracking**: Records who audited the prescription and when
- **Audit Notes**: Add detailed notes explaining the audit decision
- **Reset Capability**: Ability to reset audit status back to pending if needed

Installation
============

To install this module, copy the ``health_prescription_audit`` folder into your Tryton modules directory, then:

1. Update the module list in your Tryton server
2. Install the module in your database

Usage
=====

1. Open a prescription order
2. In the **Auditing** section at the bottom of the form:
   - View the current audit status
   - Add audit notes if needed
3. Use the action buttons:
   - **Approve**: Mark prescription as aprobada (approved)
   - **Reject**: Mark prescription as rechazada (rejected)
   - **Reset Audit**: Return audit status to pending

When you approve or reject a prescription, the system automatically:
- Records your user ID as the auditor
- Timestamps the audit action
- Displays audit information in read-only fields

Fields
======

- **audit_state**: Current auditing status (Pending Audit, Aprobada, or Rechazada)
- **audit_date**: Date and time when the prescription was audited
- **audit_user**: User who performed the audit
- **audit_notes**: Detailed notes about the audit decision

License
=======

This module is licensed under the GNU General Public License v3.0 or later (GPLv3+).
