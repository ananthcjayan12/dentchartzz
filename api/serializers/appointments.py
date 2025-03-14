from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Appointment, Patient
from api.serializers.patients import PatientSerializer

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (simplified version for appointments)"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']
        read_only_fields = ['id', 'username', 'email']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Appointment model.
    Used for list views and includes essential fields with patient and dentist details.
    """
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    dentist_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.IntegerField(source='duration', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'dentist', 'dentist_name',
            'date', 'start_time', 'end_time', 'status', 'status_display',
            'duration_minutes'
        ]
        read_only_fields = ['id', 'patient_name', 'dentist_name', 'status_display', 'duration_minutes']
    
    def get_dentist_name(self, obj):
        if obj.dentist:
            return f"{obj.dentist.first_name} {obj.dentist.last_name}".strip() or obj.dentist.username
        return ""

class AppointmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Appointment model.
    Used for detail views and includes all fields with related objects.
    """
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    dentist = UserSerializer(read_only=True)
    dentist_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='dentist'
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.IntegerField(source='duration', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_id', 'dentist', 'dentist_id',
            'date', 'start_time', 'end_time', 'status', 'status_display',
            'duration_minutes', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status_display', 'duration_minutes', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate that end_time is after start_time and that the appointment doesn't overlap
        with existing appointments for the same dentist.
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        date = data.get('date')
        dentist = data.get('dentist')
        
        # Check if end_time is after start_time
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time")
        
        # Check for overlapping appointments for the same dentist
        if start_time and end_time and date and dentist:
            # Get the appointment being updated (if any)
            instance = self.instance
            
            # Query for overlapping appointments
            overlapping = Appointment.objects.filter(
                dentist=dentist,
                date=date,
                status='scheduled'
            ).exclude(
                # Exclude the current appointment if updating
                id=instance.id if instance else None
            )
            
            # Check for overlaps
            for appt in overlapping:
                # Check if the new appointment overlaps with an existing one
                if (
                    (start_time <= appt.start_time < end_time) or  # New appointment starts before and ends during/after existing
                    (start_time < appt.end_time <= end_time) or    # New appointment starts during and ends after existing
                    (appt.start_time <= start_time < appt.end_time) or  # Existing appointment starts before and ends during/after new
                    (appt.start_time < end_time <= appt.end_time)      # Existing appointment starts during and ends after new
                ):
                    raise serializers.ValidationError(
                        f"This appointment overlaps with an existing appointment for {dentist.get_full_name()} "
                        f"on {date} from {appt.start_time} to {appt.end_time}"
                    )
        
        return data 