# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import fields, ModelView
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Or
from trytond.transaction import Transaction
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
    ], 'Audit Status', sort=False,
        states={
            'readonly': True,
            'invisible': ~Bool(Eval('is_auditor', False)),
        },
        depends=['is_auditor'],
        help='Auditing status for the prescription')

    audit_notes = fields.Text('Audit Notes',
        states={
            'readonly': Eval('audit_state') != 'pending',
            'invisible': ~Bool(Eval('is_auditor', False)),
        },
        depends=['audit_state', 'is_auditor'],
        help='Notes about the audit decision')

    audit_date = fields.DateTime('Audit Date',
        states={
            'readonly': True,
            'invisible': ~Bool(Eval('is_auditor', False)),
        },
        depends=['is_auditor'],
        help='Date when the prescription was audited')

    audit_user = fields.Many2One('res.user', 'Auditor',
        states={
            'readonly': True,
            'invisible': ~Bool(Eval('is_auditor', False)),
        },
        depends=['is_auditor'],
        help='User who performed the audit')

    is_auditor = fields.Function(
        fields.Boolean('Is Auditor'),
        'get_is_auditor')

    @classmethod
    def get_is_auditor(cls, prescriptions, name):
        pool = Pool()
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')
        try:
            group_id = ModelData.get_id('test_module', 'group_prescription_auditor')
        except KeyError:
            logger.warning('get_is_auditor: group_prescription_auditor not found in ir.model.data')
            return {p.id: False for p in prescriptions}
        user = User(Transaction().user)
        user_group_ids = [g.id for g in user.groups]
        is_aud = group_id in user_group_ids
        logger.info(f'get_is_auditor: user={user.name} group_id={group_id} user_groups={user_group_ids} result={is_aud}')
        return {p.id: is_aud for p in prescriptions}

    @staticmethod
    def default_audit_state():
        return 'pending'

    @classmethod
    def __setup__(cls):
        super(PatientPrescriptionOrder, cls).__setup__()
        cls._buttons.update({
            'approve_prescription': {
                'invisible': Or(
                    Eval('audit_state') != 'pending',
                    ~Bool(Eval('is_auditor', False)),
                ),
                'depends': ['audit_state', 'is_auditor'],
            },
            'reject_prescription': {
                'invisible': Or(
                    Eval('audit_state') != 'pending',
                    ~Bool(Eval('is_auditor', False)),
                ),
                'depends': ['audit_state', 'is_auditor'],
            },
            'reset_audit': {
                'invisible': Or(
                    Eval('audit_state') == 'pending',
                    ~Bool(Eval('is_auditor', False)),
                ),
                'depends': ['audit_state', 'is_auditor'],
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
