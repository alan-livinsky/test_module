# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import fields, ModelView
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Equal, Or
from trytond.transaction import Transaction
from trytond import backend
import logging

__all__ = ['PatientPrescriptionOrder']
logger = logging.getLogger(__name__)


class PatientPrescriptionOrder(metaclass=PoolMeta):
    'Prescription Order - Add Auditing States'
    __name__ = 'gnuhealth.prescription.order'

    audit_state = fields.Selection([
        ('pending', 'Pending Audit'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ], 'Audit Status', readonly=True, sort=False,
       help='Auditing status for the prescription')

    audit_notes = fields.Text('Audit Notes', 
        states={'readonly': Eval('audit_state') != 'pending'},
        depends=['audit_state'],
        help='Notes about the audit decision')

    audit_date = fields.DateTime('Audit Date', readonly=True,
        help='Date when the prescription was audited')

    audit_user = fields.Many2One('res.user', 'Auditor', readonly=True,
        help='User who performed the audit')

    @staticmethod
    def default_audit_state():
        return 'pending'

    @classmethod
    def __setup__(cls):
        super(PatientPrescriptionOrder, cls).__setup__()
        cls._buttons.update({
            'approve_prescription': {
                'invisible': Eval('audit_state') != 'pending',
                'depends': ['audit_state'],
            },
            'reject_prescription': {
                'invisible': Eval('audit_state') != 'pending',
                'depends': ['audit_state'],
            },
            'reset_audit': {
                'invisible': Eval('audit_state') == 'pending',
                'depends': ['audit_state'],
            },
        })

    @classmethod
    @ModelView.button
    def approve_prescription(cls, prescriptions):
        """Set prescription as aprobada (approved)"""
        from datetime import datetime
        User = Pool().get('res.user')

        current_user = User(Transaction().user)

        cls.write(prescriptions, {
            'audit_state': 'aprobada',
            'audit_date': datetime.now(),
            'audit_user': current_user.id,
        })
        
        logger.info(f'Prescription(s) approved by user {current_user.name}')

    @classmethod
    @ModelView.button
    def reject_prescription(cls, prescriptions):
        """Set prescription as rechazada (rejected)"""
        from datetime import datetime
        User = Pool().get('res.user')

        current_user = User(Transaction().user)

        cls.write(prescriptions, {
            'audit_state': 'rechazada',
            'audit_date': datetime.now(),
            'audit_user': current_user.id,
        })
        
        logger.info(f'Prescription(s) rejected by user {current_user.name}')

    @classmethod
    @ModelView.button
    def reset_audit(cls, prescriptions):
        """Reset prescription audit status back to pending"""
        cls.write(prescriptions, {
            'audit_state': 'pending',
            'audit_date': None,
            'audit_user': None,
        })
        
        logger.info('Prescription(s) audit status reset to pending')
