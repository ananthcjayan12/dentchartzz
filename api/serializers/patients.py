from rest_framework import serializers
from api.models import Patient

class PatientSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Patient model.
    Used for list views and includes only essential fields.
    """
    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'gender', 'phone', 'email']
        read_only_fields = ['id']

class PatientDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Patient model.
    Used for detail views and includes all fields.
    """
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'date_of_birth', 'phone', 'email', 'address',
            'chief_complaint', 'medical_history', 'drug_allergies', 'previous_dental_work',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 