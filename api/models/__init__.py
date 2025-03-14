# Import models here for easy access
from api.models.clinics import Clinic, ClinicMembership
from api.models.patients import Patient
from api.models.appointments import Appointment
from api.models.teeth import Tooth, ToothCondition
from api.models.treatments import Treatment, TreatmentHistory
from api.models.payments import Payment, PaymentItem

# This allows importing directly from api.models
__all__ = [
    'Clinic',
    'ClinicMembership',
    'Patient',
    'Appointment',
    'Tooth',
    'ToothCondition',
    'Treatment',
    'TreatmentHistory',
    'Payment',
    'PaymentItem',
] 