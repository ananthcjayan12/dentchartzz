from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Payment, PaymentItem, Patient, Appointment, Treatment
from api.serializers.patients import PatientSerializer
from api.serializers.appointments import AppointmentSerializer, UserSerializer
from decimal import Decimal

class PaymentItemSerializer(serializers.ModelSerializer):
    """Serializer for PaymentItem model"""
    treatment_description = serializers.CharField(source='treatment.description', read_only=True)
    
    class Meta:
        model = PaymentItem
        fields = ['id', 'description', 'amount', 'treatment', 'treatment_description']
        read_only_fields = ['id', 'treatment_description']

class PaymentSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Payment model.
    Used for list views and includes essential fields with related object names.
    """
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'patient', 'patient_name', 'payment_date', 'total_amount',
            'amount_paid', 'balance', 'payment_method', 'payment_method_display',
            'created_by', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'patient_name', 'created_by_name', 'payment_method_display',
            'balance'
        ]

class PaymentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Payment model.
    Used for detail views and includes all fields with related objects.
    """
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        write_only=True,
        source='appointment',
        required=False,
        allow_null=True
    )
    created_by = UserSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_balance_payment = serializers.BooleanField(read_only=True)
    items = PaymentItemSerializer(many=True, read_only=True)
    
    # For creating/updating payment items
    payment_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'patient', 'patient_id', 'appointment', 'appointment_id',
            'payment_date', 'total_amount', 'amount_paid', 'balance',
            'payment_method', 'payment_method_display', 'is_balance_payment',
            'notes', 'created_by', 'created_at', 'updated_at',
            'items', 'payment_items'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'payment_method_display', 'balance', 'is_balance_payment', 'items'
        ]
    
    def validate(self, data):
        """
        Validate that the patient and appointment belong to the same clinic.
        """
        # Get the clinic from the context
        clinic = self.context.get('clinic')
        
        if not clinic:
            raise serializers.ValidationError("Clinic context is required")
        
        # Check if the patient belongs to the clinic
        patient = data.get('patient')
        if patient and patient.clinic != clinic:
            raise serializers.ValidationError("Patient does not belong to this clinic")
        
        # Check if the appointment belongs to the clinic
        appointment = data.get('appointment')
        if appointment and appointment.clinic != clinic:
            raise serializers.ValidationError("Appointment does not belong to this clinic")
        
        # Check if the appointment is for the same patient
        if patient and appointment and appointment.patient != patient:
            raise serializers.ValidationError("Appointment is not for this patient")
        
        return data
    
    def create(self, validated_data):
        """
        Create a payment with payment items.
        """
        # Extract payment items data
        payment_items_data = validated_data.pop('payment_items', [])
        
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        
        # Create the payment
        payment = Payment.objects.create(**validated_data)
        
        # Create payment items
        for item_data in payment_items_data:
            treatment_id = item_data.pop('treatment_id', None)
            treatment = None
            
            if treatment_id:
                try:
                    treatment = Treatment.objects.get(id=treatment_id, clinic=payment.clinic)
                except Treatment.DoesNotExist:
                    pass
            
            PaymentItem.objects.create(
                payment=payment,
                treatment=treatment,
                **item_data
            )
        
        return payment
    
    def update(self, instance, validated_data):
        """
        Update a payment with payment items.
        """
        # Extract payment items data
        payment_items_data = validated_data.pop('payment_items', None)
        
        # Update the payment
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update payment items if provided
        if payment_items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in payment_items_data:
                treatment_id = item_data.pop('treatment_id', None)
                treatment = None
                
                if treatment_id:
                    try:
                        treatment = Treatment.objects.get(id=treatment_id, clinic=instance.clinic)
                    except Treatment.DoesNotExist:
                        pass
                
                PaymentItem.objects.create(
                    payment=instance,
                    treatment=treatment,
                    **item_data
                )
        
        return instance 

class PaymentSummarySerializer(serializers.Serializer):
    """
    Serializer for payment summary data.
    Used for aggregating payment information for a patient.
    """
    total_billed = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    last_payment_date = serializers.DateField(allow_null=True)
    
    def to_representation(self, instance):
        """
        Handle potential None values in the data.
        """
        data = super().to_representation(instance)
        # Convert string values to Decimal objects
        for field in ['total_billed', 'total_paid', 'balance_due']:
            if data.get(field) is None:
                data[field] = Decimal('0')
        return data 