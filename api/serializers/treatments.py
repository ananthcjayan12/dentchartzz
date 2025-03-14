from rest_framework import serializers
from api.models import Treatment, Tooth, ToothCondition, Patient, Appointment
from api.serializers.patients import PatientSerializer
from api.serializers.appointments import AppointmentSerializer

class ToothSerializer(serializers.ModelSerializer):
    """Serializer for Tooth model"""
    quadrant_display = serializers.CharField(source='get_quadrant_display', read_only=True)
    
    class Meta:
        model = Tooth
        fields = ['id', 'number', 'name', 'quadrant', 'quadrant_display', 'position']
        read_only_fields = ['id', 'quadrant_display']

class ToothConditionSerializer(serializers.ModelSerializer):
    """Serializer for ToothCondition model"""
    class Meta:
        model = ToothCondition
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class TreatmentSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Treatment model.
    Used for list views and includes essential fields with related object names.
    """
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    tooth_number = serializers.IntegerField(source='tooth.number', read_only=True)
    tooth_name = serializers.CharField(source='tooth.name', read_only=True)
    condition_name = serializers.CharField(source='condition.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Treatment
        fields = [
            'id', 'patient', 'patient_name', 'tooth', 'tooth_number', 'tooth_name',
            'condition', 'condition_name', 'description', 'status', 'status_display',
            'cost'
        ]
        read_only_fields = [
            'id', 'patient_name', 'tooth_number', 'tooth_name', 'condition_name',
            'status_display'
        ]

class TreatmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Treatment model.
    Used for detail views and includes all fields with related objects.
    """
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    tooth = ToothSerializer(read_only=True)
    tooth_id = serializers.PrimaryKeyRelatedField(
        queryset=Tooth.objects.all(),
        write_only=True,
        source='tooth',
        required=False,
        allow_null=True
    )
    condition = ToothConditionSerializer(read_only=True)
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=ToothCondition.objects.all(),
        write_only=True,
        source='condition'
    )
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        write_only=True,
        source='appointment',
        required=False,
        allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Treatment
        fields = [
            'id', 'patient', 'patient_id', 'tooth', 'tooth_id', 'condition', 'condition_id',
            'appointment', 'appointment_id', 'description', 'status', 'status_display',
            'cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status_display', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate that the patient, tooth, condition, and appointment belong to the same clinic.
        """
        # Get the clinic from the context
        clinic = self.context.get('clinic')
        
        if not clinic:
            raise serializers.ValidationError("Clinic context is required")
        
        # Check if the patient belongs to the clinic
        patient = data.get('patient')
        if patient and patient.clinic != clinic:
            raise serializers.ValidationError("Patient does not belong to this clinic")
        
        # Check if the condition belongs to the clinic
        condition = data.get('condition')
        if condition and condition.clinic != clinic:
            raise serializers.ValidationError("Tooth condition does not belong to this clinic")
        
        # Check if the appointment belongs to the clinic
        appointment = data.get('appointment')
        if appointment and appointment.clinic != clinic:
            raise serializers.ValidationError("Appointment does not belong to this clinic")
        
        # Check if the appointment is for the same patient
        if patient and appointment and appointment.patient != patient:
            raise serializers.ValidationError("Appointment is not for this patient")
        
        return data 