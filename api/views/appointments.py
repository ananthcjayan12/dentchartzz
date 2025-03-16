from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, date
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
        Get available time slots for a dentist on a specific date.
        
        This endpoint returns a list of time slots from 9 AM to 5 PM in 30-minute intervals,
        marking slots that overlap with existing appointments as unavailable.
        """
        try:
            dentist_id = request.query_params.get('dentist')
            date_str = request.query_params.get('date')
            selected_time = request.query_params.get('selected_time', '')
            
            if not dentist_id or not date_str:
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse the date
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Generate time slots from 9 AM to 5 PM in 30-minute intervals
            time_slots = []
            start_hour = 9  # 9 AM
            end_hour = 17   # 5 PM
            
            current_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=start_hour)
            end_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=end_hour)
            
            while current_time < end_time:
                time_slots.append({
                    'time': current_time.time().strftime('%H:%M'),
                    'display': current_time.strftime('%I:%M %p'),
                    'available': True,
                    'selected': current_time.time().strftime('%H:%M') == selected_time
                })
                current_time += timedelta(minutes=30)
            
            # Get the clinic from the URL
            clinic = self.get_clinic_from_url()
            
            # Mark booked slots as unavailable
            booked_appointments = Appointment.objects.filter(
                clinic=clinic,
                dentist_id=dentist_id,
                date=selected_date,
                status='scheduled'
            )
            
            # If we're editing an existing appointment, exclude it from the booked appointments
            appointment_id = request.query_params.get('appointment_id')
            if appointment_id:
                booked_appointments = booked_appointments.exclude(pk=appointment_id)
            
            for appointment in booked_appointments:
                # Mark all slots that overlap with this appointment as unavailable
                for slot in time_slots:
                    slot_time = datetime.strptime(slot['time'], '%H:%M').time()
                    slot_start = datetime.combine(selected_date, slot_time)
                    slot_end = slot_start + timedelta(minutes=30)
                    appointment_start = datetime.combine(selected_date, appointment.start_time)
                    appointment_end = datetime.combine(selected_date, appointment.end_time)
                    
                    if (slot_start < appointment_end and slot_end > appointment_start):
                        slot['available'] = False
            
            return Response({'time_slots': time_slots})
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 