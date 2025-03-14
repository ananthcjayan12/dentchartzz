from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from api.models import Appointment
from api.views.base import ClinicModelViewSet
from api.serializers.appointments import AppointmentSerializer, AppointmentDetailSerializer

class AppointmentViewSet(ClinicModelViewSet):
    """
    ViewSet for managing appointments within a clinic.
    
    This ViewSet provides CRUD operations for appointments and ensures that
    users can only access appointments from clinics they are members of.
    """
    queryset = Appointment.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'dentist__username', 'dentist__first_name', 'dentist__last_name', 'notes']
    
    def get_queryset(self):
        """
        Filter appointments by clinic and optionally by date range, status, patient, or dentist.
        """
        queryset = super().get_queryset()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        status_param = self.request.query_params.get('status')
        patient_id = self.request.query_params.get('patient_id')
        dentist_id = self.request.query_params.get('dentist_id')
        today = self.request.query_params.get('today')
        upcoming = self.request.query_params.get('upcoming')
        
        # Filter by date range
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by status
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by patient
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by dentist
        if dentist_id:
            queryset = queryset.filter(dentist_id=dentist_id)
        
        # Filter for today's appointments
        if today:
            today_date = timezone.now().date()
            queryset = queryset.filter(date=today_date)
        
        # Filter for upcoming appointments
        if upcoming:
            today_date = timezone.now().date()
            queryset = queryset.filter(
                Q(date__gt=today_date) | 
                Q(date=today_date, start_time__gte=timezone.now().time())
            ).filter(status='scheduled')
        
        return queryset.order_by('date', 'start_time')
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action.
        
        For list actions, use the basic AppointmentSerializer.
        For retrieve, update, and create actions, use the detailed AppointmentDetailSerializer.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return AppointmentDetailSerializer
        return AppointmentSerializer
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, clinic_id=None, pk=None):
        """
        Cancel an appointment.
        """
        appointment = self.get_object()
        
        # Check if the appointment is already cancelled
        if appointment.status == 'cancelled':
            return Response(
                {'detail': 'This appointment is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the status to cancelled
        appointment.status = 'cancelled'
        appointment.save()
        
        # Return the updated appointment
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, clinic_id=None, pk=None):
        """
        Update the status of an appointment.
        """
        appointment = self.get_object()
        
        # Get the new status from the request data
        new_status = request.data.get('status')
        
        # Validate the new status
        if not new_status:
            return Response(
                {'detail': 'Status is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return Response(
                {'detail': f'Invalid status. Must be one of: {", ".join(dict(Appointment.STATUS_CHOICES).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the status
        appointment.status = new_status
        appointment.save()
        
        # Return the updated appointment
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def time_slots(self, request, clinic_id=None):
        """
        Get available time slots for a specific date and dentist.
        """
        # Get query parameters
        date = request.query_params.get('date')
        dentist_id = request.query_params.get('dentist_id')
        
        # Validate parameters
        if not date:
            return Response(
                {'detail': 'Date is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not dentist_id:
            return Response(
                {'detail': 'Dentist ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # Get all scheduled appointments for the dentist on the specified date
        appointments = Appointment.objects.filter(
            clinic=clinic,
            dentist_id=dentist_id,
            date=date,
            status='scheduled'
        ).order_by('start_time')
        
        # Define the working hours (9 AM to 5 PM by default)
        # This could be customized based on clinic settings
        working_hours_start = '09:00:00'
        working_hours_end = '17:00:00'
        
        # Define the slot duration in minutes (30 minutes by default)
        slot_duration = 30
        
        # Generate all possible time slots
        from datetime import datetime, timedelta
        
        # Parse the working hours
        start_time = datetime.strptime(working_hours_start, '%H:%M:%S').time()
        end_time = datetime.strptime(working_hours_end, '%H:%M:%S').time()
        
        # Create a datetime object for the start time
        start_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), start_time)
        end_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), end_time)
        
        # Generate all slots
        slots = []
        current = start_datetime
        
        while current + timedelta(minutes=slot_duration) <= end_datetime:
            slot_end = current + timedelta(minutes=slot_duration)
            
            # Check if the slot overlaps with any existing appointment
            is_available = True
            
            for appt in appointments:
                appt_start = datetime.combine(appt.date, appt.start_time)
                appt_end = datetime.combine(appt.date, appt.end_time)
                
                # Check for overlap
                if (
                    (current <= appt_start < slot_end) or
                    (current < appt_end <= slot_end) or
                    (appt_start <= current < appt_end) or
                    (appt_start < slot_end <= appt_end)
                ):
                    is_available = False
                    break
            
            # Add the slot to the list if it's available
            if is_available:
                slots.append({
                    'start_time': current.time().strftime('%H:%M:%S'),
                    'end_time': slot_end.time().strftime('%H:%M:%S')
                })
            
            # Move to the next slot
            current = slot_end
        
        return Response(slots) 