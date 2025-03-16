from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, date
from api.models import Appointment, ClinicMembership
from api.views.base import ClinicModelViewSet
from api.serializers.appointments import AppointmentSerializer, AppointmentDetailSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

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
    
    @action(detail=False, methods=['get'], url_path='time_slots')
    def time_slots(self, request, clinic_id=None):
        """Get available time slots for a given date and dentist."""
        clinic = self.get_clinic_from_url()
        
        # Validate required parameters
        date_str = request.query_params.get('date')
        dentist_id = request.query_params.get('dentist_id') or request.query_params.get('dentist')
        
        if not date_str or not dentist_id:
            return Response(
                {'error': 'Both date and dentist_id are required parameters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse the date
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Validate the dentist
            dentist = get_object_or_404(User, id=dentist_id)
            
            # Check if the dentist is associated with this clinic
            if not ClinicMembership.objects.filter(
                user=dentist, clinic=clinic, role__in=['dentist', 'administrator']
            ).exists():
                return Response(
                    {'error': 'The specified dentist is not associated with this clinic.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the clinic's working hours for the day of the week
            day_of_week = appointment_date.strftime('%A').lower()
            working_hours = getattr(clinic, f"{day_of_week}_hours", None)
            
            # Use default hours if not set
            if not working_hours:
                working_hours = "09:00 - 17:00"
            elif working_hours.lower() == "closed":
                return Response(
                    {'error': f'The clinic is closed on {day_of_week.capitalize()}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse working hours
            start_time_str, end_time_str = working_hours.split('-')
            start_time = datetime.strptime(start_time_str.strip(), '%H:%M').time()
            end_time = datetime.strptime(end_time_str.strip(), '%H:%M').time()
            
            # Generate time slots
            time_slots = []
            current_time = datetime.combine(appointment_date, start_time)
            end_datetime = datetime.combine(appointment_date, end_time)
            selected_time = request.query_params.get('selected_time')
            
            while current_time < end_datetime:
                # Check if this time slot is already booked
                slot_end_time = current_time + timedelta(minutes=30)
                is_booked = Appointment.objects.filter(
                    clinic=clinic,
                    dentist=dentist,
                    date=appointment_date,
                    start_time__lt=slot_end_time.time(),
                    end_time__gt=current_time.time()
                ).exists()
                
                time_str = current_time.strftime('%H:%M')
                time_slots.append({
                    'time': time_str,
                    'display': time_str,  # Add display field for compatibility
                    'available': not is_booked,  # Use 'available' instead of 'is_available'
                    'selected': selected_time == time_str if selected_time else False
                })
                
                current_time += timedelta(minutes=30)
            
            # Return the time slots in the format expected by the tests
            return Response({'time_slots': time_slots})
        
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            ) 