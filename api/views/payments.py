from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from api.models import Payment
from api.views.base import ClinicModelViewSet
from api.serializers.payments import PaymentSerializer, PaymentDetailSerializer

class PaymentViewSet(ClinicModelViewSet):
    """
    ViewSet for managing payments within a clinic.
    
    This ViewSet provides CRUD operations for payments and ensures that
    users can only access payments from clinics they are members of.
    """
    queryset = Payment.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'notes']
    
    def get_queryset(self):
        """
        Filter payments by clinic and optionally by patient, date range, or payment method.
        """
        queryset = super().get_queryset()
        
        # Get query parameters
        patient_id = self.request.query_params.get('patient_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        payment_method = self.request.query_params.get('payment_method')
        
        # Filter by patient
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by date range
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        # Filter by payment method
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset.order_by('-payment_date', '-created_at')
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action.
        
        For list actions, use the basic PaymentSerializer.
        For retrieve, update, and create actions, use the detailed PaymentDetailSerializer.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return PaymentDetailSerializer
        return PaymentSerializer
    
    def get_serializer_context(self):
        """
        Add the clinic to the serializer context.
        """
        context = super().get_serializer_context()
        context['clinic'] = self.get_clinic_from_url()
        return context
    
    @action(detail=False, methods=['get'])
    def patient_balance(self, request, clinic_id=None):
        """
        Get the balance for a specific patient.
        """
        # Get query parameters
        patient_id = request.query_params.get('patient_id')
        
        # Validate parameters
        if not patient_id:
            return Response(
                {'detail': 'Patient ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # Get all payments for the patient
        payments = Payment.objects.filter(
            clinic=clinic,
            patient_id=patient_id
        )
        
        # Calculate total amount and total paid
        total_amount = payments.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Calculate balance
        balance = total_amount - total_paid
        
        return Response({
            'patient_id': patient_id,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'balance': balance
        })
    
    @action(detail=False, methods=['get'])
    def patient_payments(self, request, clinic_id=None):
        """
        Get all payments for a specific patient.
        """
        # Get query parameters
        patient_id = request.query_params.get('patient_id')
        
        # Validate parameters
        if not patient_id:
            return Response(
                {'detail': 'Patient ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # Get all payments for the patient
        payments = Payment.objects.filter(
            clinic=clinic,
            patient_id=patient_id
        ).order_by('-payment_date', '-created_at')
        
        # Serialize the payments
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data) 