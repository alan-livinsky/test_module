# Documentación del Módulo health_prescription_audit

## Propósito del Módulo

Este módulo extiende el modelo `gnuhealth.prescription.order` de GNU Health para agregar funcionalidad de auditoría de recetas médicas. Permite que usuarios con el rol "Prescription Auditor" puedan aprobar, rechazar o restablecer el estado de auditoría de las recetas.

---

## Archivos del Módulo

### 1. `__init__.py`
**Propósito:** Punto de entrada del módulo Tryton. Registra el modelo `PatientPrescriptionOrder` en el pool de la aplicación.

**Funcionalidad:**
- Importa el módulo `health_prescription_audit`
- Registra el modelo `PatientPrescriptionOrder` con el tipo 'model'

---

### 2. `health_prescription_audit.py`
**Propósito:** Define la clase del modelo que extiende `gnuhealth.prescription.order` con campos y métodos de auditoría.

**Campos agregados:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `audit_state` | Selection | Estado de auditoría: 'pending', 'aprobada', 'rechazada' |
| `audit_notes` | Text | Notas sobre la decisión de auditoría |
| `audit_date` | DateTime | Fecha en que se realizó la auditoría |
| `audit_user` | Many2One | Usuario que realizó la auditoría |
| `is_auditor` | Function (Boolean) | Indica si el usuario actual es auditor |

**Métodos principales:**
- `get_is_auditor()`: Verifica si el usuario pertenece al grupo `group_prescription_auditor`
- `approve_prescription()`: Marca receta como aprobada
- `reject_prescription()`: Marca receta como rechazada
- `reset_audit()`: Restablece el estado a pending

**Posibles errores:**
- Si `group_prescription_auditor` no existe en `ir.model.data`, `get_is_auditor` retorna `False` para todos los registros. Esto podría ocultar la funcionalidad de auditoría sin notificación clara al administrador.

---

### 3. `health_prescription_audit_view.xml`
**Propósito:** Define la vista XML para el módulo Tryton - crea registros de UI, grupos, permisos y reglas de botones.

**Elementos creados:**
- Vista `prescription_audit_form` que hereda de `health.gnuhealth_prescription_view`
- Grupo `group_prescription_auditor` con permisos de lectura/escritura
- Reglas de botones para `approve_prescription`, `reject_prescription`, `reset_audit`

**Posibles errores:**
- Referencia `health.gnuhealth_prescription_view` - si esta vista no existe, el módulo fallará al actualizarse
- Los `ir.model.field.access` y `ir.model.button.rule` pueden fallar si los campos no están correctamente definidos en el modelo Python

---

### 4. `view/prescription_audit_form.xml`
**Propósito:** Define la interfaz de usuario para los campos de auditoría usando XPath.

**Elementos UI:**
- Grupo "Auditing" con campos: audit_state, audit_date, audit_user
- Grupo "Audit Actions" con botones: Approve, Reject, Reset Audit
- Campo audit_notes

**Posibles errores:**
- XPath `/form/group[@id='group_prescription_notes']` - si el grupo con este ID no existe en la vista heredada, la inserción XPath fallará silenciosamente
- Los campos dependen de `is_auditor` pero no se verifica si este campo está disponible en todos los contextos

---

### 5. `tests/__init__.py`
**Propósito:** Define pruebas unitarias para el módulo.

**Pruebas:**
- `test_prescription_audit_states`: Verifica que los campos de auditoría existen en el modelo

**Posibles errores:**
- `activate_module('health_prescription_audit')` - usa el nombre del módulo en string en lugar del nombre real del paquete Python (`test_module`)

---

### 6. `setup.py`
**Propósito:** Configuración del paquete para distribución via setuptools.

**Observación:**
- El `entry_points` registra el módulo como `health_prescription_audit` pero el directorio del módulo es `test_module`. Esto puede causar conflictos de importación.

---

## Bugs Potenciales Identificados

1. **Inconsistencia de nombres:** `setup.py` menciona `health_prescription_audit` en entry_points pero el directorio real es `test_module`

2. **XPath frágil:** `view/prescription_audit_form.xml` depende de que exista un grupo con `id='group_prescription_notes'` en la vista heredada

3. **Manejo de errores silencioso:** `get_is_auditor` retorna `False` cuando el grupo no existe, sin notificar al administrador

4. **Test con nombre incorrecto:** `tests/__init__.py` activa `'health_prescription_audit'` pero el módulo se llama `test_module`

5. **Sin validación de estado:** Los botones no validan que el usuario tenga permisos adicionales más allá de pertenecer al grupo
