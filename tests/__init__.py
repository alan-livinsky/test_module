# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from trytond.tests.test_tryton import activate_module, DB_NAME, USER
from trytond.pool import Pool


class HealthPrescriptionAuditTestCase(unittest.TestCase):
    """Test Health Prescription Audit module"""

    @classmethod
    def setUpClass(cls):
        activate_module('health_prescription_audit')

    def test_prescription_audit_states(self):
        """Test that prescription audit states are available"""
        pool = Pool()
        PatientPrescriptionOrder = pool.get('gnuhealth.prescription.order')
        
        # Check that audit_state field exists
        assert hasattr(PatientPrescriptionOrder, 'audit_state')
        assert hasattr(PatientPrescriptionOrder, 'audit_notes')
        assert hasattr(PatientPrescriptionOrder, 'audit_date')
        assert hasattr(PatientPrescriptionOrder, 'audit_user')


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HealthPrescriptionAuditTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
