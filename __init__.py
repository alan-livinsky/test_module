# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.pool import Pool
from . import health_prescription_audit


def register():
    Pool.register(
        health_prescription_audit.PatientPrescriptionOrder,
        module='test_module', type_='model')
