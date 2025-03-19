from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from api.views.base import ClinicModelViewSet
from api.models import Patient, Appointment, Payment
from api.serializers.stats import PatientStatsSerializer, AppointmentStatsSerializer

class ClinicStatsViewSet(ClinicModelViewSet):
    """
    ViewSet for clinic statistics and dashboard data.
    """
    
    @action(detail=False, methods=['GET'], url_path='patients')
    def patient_stats(self, request, clinic_id=None):
        """Get patient statistics for the clinic dashboard"""
        try:
            now = timezone.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            three_months_ago = now - timedelta(days=90)
            
            # Get total patients
            total_patients = Patient.objects.filter(clinic_id=clinic_id).count()
            
            # Get new patients this month
            new_patients = Patient.objects.filter(
                clinic_id=clinic_id,
                created_at__gte=start_of_month
            ).count()
            
            # Get last month's patient count for growth calculation
            last_month = start_of_month - timedelta(days=1)
            last_month_start = last_month.replace(day=1)
            last_month_patients = Patient.objects.filter(
                clinic_id=clinic_id,
                created_at__lt=start_of_month
            ).count()
            
            # Calculate monthly growth
            monthly_growth = 0
            if last_month_patients > 0:
                monthly_growth = (new_patients / last_month_patients) * 100
            
            # Get active patients (with appointments in last 3 months)
            active_patients = Patient.objects.filter(
                clinic_id=clinic_id,
                appointments__date__gte=three_months_ago
            ).distinct().count()
            
            stats = {
                'totalPatients': total_patients,
                'monthlyGrowth': round(monthly_growth, 1),
                'newPatientsThisMonth': new_patients,
                'activePatients': active_patients
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['GET'], url_path='appointments')
    def appointment_stats(self, request, clinic_id=None):
        """Get appointment statistics for the clinic dashboard"""
        try:
            now = timezone.now()
            today = now.date()
            yesterday = today - timedelta(days=1)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get today's appointments
            today_count = Appointment.objects.filter(
                clinic_id=clinic_id,
                date=today
            ).count()
            
            # Get yesterday's appointments
            yesterday_count = Appointment.objects.filter(
                clinic_id=clinic_id,
                date=yesterday
            ).count()
            
            # Calculate daily change
            daily_change = today_count - yesterday_count
            
            # Get monthly revenue
            monthly_revenue = Payment.objects.filter(
                clinic_id=clinic_id,
                payment_date__gte=start_of_month
            ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
            
            # Get last month's revenue
            last_month = start_of_month - timedelta(days=1)
            last_month_start = last_month.replace(day=1)
            last_month_revenue = Payment.objects.filter(
                clinic_id=clinic_id,
                payment_date__gte=last_month_start,
                payment_date__lt=start_of_month
            ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
            
            # Calculate revenue change
            revenue_change = 0
            if last_month_revenue > 0:
                revenue_change = ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100
            
            # Get completion rates
            completed_treatments = Appointment.objects.filter(
                clinic_id=clinic_id,
                date__gte=start_of_month,
                status='completed'
            ).count()
            
            total_treatments = Appointment.objects.filter(
                clinic_id=clinic_id,
                date__gte=start_of_month
            ).exclude(status='cancelled').count()
            
            completion_rate = 0
            if total_treatments > 0:
                completion_rate = (completed_treatments / total_treatments) * 100
            
            # Get upcoming appointments
            upcoming_count = Appointment.objects.filter(
                clinic_id=clinic_id,
                date__gt=today
            ).count()
            
            # Get cancelled appointments this month
            cancelled_count = Appointment.objects.filter(
                clinic_id=clinic_id,
                date__gte=start_of_month,
                status='cancelled'
            ).count()
            
            stats = {
                'todayCount': today_count,
                'dailyChange': daily_change,
                'monthlyRevenue': monthly_revenue,
                'revenueChange': round(revenue_change, 1),
                'completionRate': round(completion_rate, 1),
                'upcomingCount': upcoming_count,
                'cancelledCount': cancelled_count
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 