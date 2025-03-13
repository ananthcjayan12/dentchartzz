from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Patient, Appointment, Treatment, Tooth, ToothCondition, TreatmentHistory, Payment, PaymentItem
from .forms import PatientForm, AppointmentForm, TreatmentForm, PaymentForm, PaymentItemFormSet
from datetime import date, datetime, timedelta
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.template.loader import render_to_string
import re

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user_profile = request.user.profile
    role = user_profile.role
    
    # Common data for all roles
    today_appointments = Appointment.objects.filter(date=date.today())
    
    context = {
        'role': role,
        'today_appointments': today_appointments,
    }
    
    # Role-specific data
    if role == 'admin':
        context['total_patients'] = Patient.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_treatments'] = Treatment.objects.count()
    elif role == 'dentist':
        context['my_appointments'] = Appointment.objects.filter(dentist=request.user)
        context['my_patients'] = Patient.objects.filter(appointments__dentist=request.user).distinct()
    
    return render(request, 'app/dashboard.html', context)

# Patient Management Views
@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        # Check if search query is a number (could be ID or phone)
        is_numeric = search_query.isdigit()
        
        # Create a query that searches across name, phone, and ID (if numeric)
        query = Q(name__icontains=search_query) | Q(phone__icontains=search_query)
        
        # Add ID search if the query is numeric
        if is_numeric:
            query |= Q(id=search_query)
            
        patients = patients.filter(query)
    
    context = {
        'patients': patients,
        'search_query': search_query,
    }
    return render(request, 'app/patient_list.html', context)

@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.name} created successfully!')
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'title': 'Add New Patient',
    }
    return render(request, 'app/patient_form.html', context)

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-start_time')
    treatments = Treatment.objects.filter(patient=patient).order_by('-created_at')
    
    # Get payment information
    payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
    recent_payments = payments[:5]  # Get the 5 most recent payments
    
    # Calculate totals
    total_treatment_cost = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_treatment_cost - total_paid
    
    # Get all teeth for the dental chart
    teeth = Tooth.objects.all().order_by('quadrant', 'position')
    
    # Add treatment status properties to each tooth
    for tooth in teeth:
        # Get all treatments for this tooth
        tooth_treatments = Treatment.objects.filter(patient=patient, tooth=tooth)
        
        # Check if the tooth has any treatments
        tooth.has_treatments = tooth_treatments.exists()
        
        # Check if the tooth has planned treatments
        tooth.has_planned_treatments = tooth_treatments.filter(status='planned').exists()
        
        # Check if the tooth has in-progress treatments
        tooth.has_in_progress_treatments = tooth_treatments.filter(status='in_progress').exists()
        
        # Check if the tooth has completed treatments
        tooth.has_completed_treatments = tooth_treatments.filter(status='completed').exists()
        
        # Count treatments by status
        tooth.treatment_counts = {
            'total': tooth_treatments.count(),
            'planned': tooth_treatments.filter(status='planned').count(),
            'in_progress': tooth_treatments.filter(status='in_progress').count(),
            'completed': tooth_treatments.filter(status='completed').count(),
            'cancelled': tooth_treatments.filter(status='cancelled').count(),
        }
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'treatments': treatments,
        'recent_payments': recent_payments,
        'total_treatment_cost': total_treatment_cost,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'teeth': teeth,
    }
    return render(request, 'app/patient_detail.html', context)

@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient {patient.name} updated successfully!')
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    
    context = {
        'form': form,
        'patient': patient,
        'title': 'Edit Patient',
    }
    return render(request, 'app/patient_form.html', context)

@login_required
def patient_create_ajax(request):
    """
    AJAX view for creating a patient from the appointment form.
    Returns JSON with the new patient's ID and name if successful,
    or the form with errors if not.
    """
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return JsonResponse({
                'success': True,
                'patient_id': patient.id,
                'patient_name': patient.name
            })
        else:
            # Return the form with errors
            html = render_to_string('app/patient_form_ajax.html', {
                'form': form,
            }, request=request)
            return JsonResponse({
                'success': False,
                'html': html
            })
    else:
        # Display the form
        form = PatientForm()
        html = render_to_string('app/patient_form_ajax.html', {
            'form': form,
        }, request=request)
        return JsonResponse({
            'success': True,
            'html': html
        }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else HttpResponse(html)

# Appointment Management Views
@login_required
def appointment_list(request):
    # Get filter parameters
    date_filter = request.GET.get('date')
    dentist_filter = request.GET.get('dentist')
    status_filter = request.GET.get('status')
    
    # Set default filters if none provided
    today = date.today()
    
    # Default to today's date if no date filter
    if not date_filter:
        date_filter = today.strftime('%Y-%m-%d')
    
    # Default to logged-in user if they are a dentist and no dentist filter
    if not dentist_filter and hasattr(request.user, 'profile') and request.user.profile.role == 'dentist':
        dentist_filter = str(request.user.id)
    
    # Default to scheduled appointments if no status filter
    if not status_filter:
        status_filter = 'scheduled'
    
    # Base queryset
    appointments = Appointment.objects.all().order_by('date', 'start_time')
    
    # Apply filters
    if date_filter:
        appointments = appointments.filter(date=date_filter)
    if dentist_filter:
        appointments = appointments.filter(dentist_id=dentist_filter)
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Get list of dentists for filter dropdown
    dentists = User.objects.filter(profile__role='dentist')
    
    context = {
        'appointments': appointments,
        'dentists': dentists,
        'status_choices': Appointment.STATUS_CHOICES,
        'current_date': date_filter,
        'default_date': today.strftime('%Y-%m-%d'),
        'default_dentist': dentist_filter,
        'default_status': status_filter,
    }
    return render(request, 'app/appointment_list.html', context)

@login_required
def appointment_calendar(request):
    # Get the week start date (default to current week)
    week_start_str = request.GET.get('week_start')
    if week_start_str:
        week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
    else:
        week_start = date.today() - timedelta(days=date.today().weekday())
    
    # Calculate week end
    week_end = week_start + timedelta(days=6)
    
    # Get all appointments for the week
    appointments = Appointment.objects.filter(
        date__range=[week_start, week_end]
    ).order_by('date', 'start_time')
    
    # Organize appointments by day
    calendar_data = {}
    current_date = week_start
    while current_date <= week_end:
        calendar_data[current_date] = appointments.filter(date=current_date)
        current_date += timedelta(days=1)
    
    context = {
        'calendar_data': calendar_data,
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': week_start - timedelta(days=7),
        'next_week': week_start + timedelta(days=7),
    }
    return render(request, 'app/appointment_calendar.html', context)

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'scheduled'
            
            # Handle chief complaint
            chief_complaint = request.POST.get('chief_complaint', '')
            if chief_complaint:
                # Add chief complaint to notes
                if appointment.notes:
                    appointment.notes += f"\n\nChief Complaint: {chief_complaint}"
                else:
                    appointment.notes = f"Chief Complaint: {chief_complaint}"
                
                # Also update patient's chief complaint if it's empty
                patient = appointment.patient
                if not patient.chief_complaint or not patient.chief_complaint.strip():
                    patient.chief_complaint = chief_complaint
                    patient.save()
            
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        # Pre-fill patient if provided in GET parameters
        initial = {}
        patient_id = request.GET.get('patient')
        date_param = request.GET.get('date')
        dentist_id = request.GET.get('dentist')
        
        # Pre-fill with today's date by default
        if date_param:
            try:
                # Try to parse the date parameter
                parsed_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                initial['date'] = parsed_date
            except ValueError:
                # If the date format is invalid, use today's date
                initial['date'] = date.today()
        else:
            initial['date'] = date.today()
            
        if patient_id:
            initial['patient'] = patient_id
            
        if dentist_id:
            initial['dentist'] = dentist_id
        # Auto-select the logged-in doctor if they are a dentist and no dentist is specified
        elif hasattr(request.user, 'profile') and request.user.profile.role == 'dentist':
            initial['dentist'] = request.user.id
            
        form = AppointmentForm(initial=initial)
    
    # Get all patients for the dropdown
    patients = Patient.objects.all().order_by('name')
    
    # Get all dentists for the dropdown
    dentists = User.objects.filter(profile__role='dentist')
    
    # Get available time slots for the selected date and dentist
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    selected_dentist_id = request.GET.get('dentist', None)
    
    # If dentist is not in request but user is a dentist, use the logged-in user
    if not selected_dentist_id and hasattr(request.user, 'profile') and request.user.profile.role == 'dentist':
        selected_dentist_id = request.user.id
        
    # Generate time slots from 9 AM to 5 PM in 30-minute intervals
    time_slots = []
    start_hour = 9  # 9 AM
    end_hour = 17   # 5 PM
    
    current_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=start_hour)
    end_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=end_hour)
    
    while current_time < end_time:
        time_slots.append({
            'time': current_time.time(),
            'display': current_time.strftime('%I:%M %p'),
            'available': True,
            'selected': False
        })
        current_time += timedelta(minutes=30)
    
    # Mark booked slots as unavailable
    if selected_date and selected_dentist_id:
        try:
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            booked_appointments = Appointment.objects.filter(
                dentist_id=selected_dentist_id,
                date=selected_date_obj,
                status='scheduled'
            )
            
            for appointment in booked_appointments:
                # Mark all slots that overlap with this appointment as unavailable
                for slot in time_slots:
                    slot_start = datetime.combine(selected_date_obj, slot['time'])
                    slot_end = slot_start + timedelta(minutes=30)
                    appointment_start = datetime.combine(selected_date_obj, appointment.start_time)
                    appointment_end = datetime.combine(selected_date_obj, appointment.end_time)
                    
                    if (slot_start < appointment_end and slot_end > appointment_start):
                        slot['available'] = False
        except (ValueError, TypeError):
            # Handle invalid date format
            pass
    
    context = {
        'form': form,
        'patients': patients,
        'dentists': dentists,
        'time_slots': time_slots,
        'selected_date': selected_date,
        'selected_dentist_id': selected_dentist_id,
        'title': 'Schedule New Appointment',
    }
    return render(request, 'app/appointment_form.html', context)

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    treatments = Treatment.objects.filter(appointment=appointment)
    
    # Get status choices for the form
    status_choices = Appointment.STATUS_CHOICES
    
    # Get payment information
    patient = appointment.patient
    payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
    recent_payments = payments[:5]  # Get the 5 most recent payments
    
    # Calculate totals
    total_treatment_cost = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_treatment_cost - total_paid
    
    # Get all teeth for the dental chart
    teeth = Tooth.objects.all().order_by('quadrant', 'position')
    
    # Add treatment status properties to each tooth
    for tooth in teeth:
        # Get all treatments for this tooth from this patient
        tooth_treatments = Treatment.objects.filter(patient=patient, tooth=tooth)
        
        # Check if the tooth has any treatments
        tooth.has_treatments = tooth_treatments.exists()
        
        # Check if the tooth has planned treatments
        tooth.has_planned_treatments = tooth_treatments.filter(status='planned').exists()
        
        # Check if the tooth has in-progress treatments
        tooth.has_in_progress_treatments = tooth_treatments.filter(status='in_progress').exists()
        
        # Check if the tooth has completed treatments
        tooth.has_completed_treatments = tooth_treatments.filter(status='completed').exists()
        
        # Count treatments by status
        tooth.treatment_counts = {
            'total': tooth_treatments.count(),
            'planned': tooth_treatments.filter(status='planned').count(),
            'in_progress': tooth_treatments.filter(status='in_progress').count(),
            'completed': tooth_treatments.filter(status='completed').count(),
            'cancelled': tooth_treatments.filter(status='cancelled').count(),
        }
        
        # Highlight teeth with treatments for this specific appointment
        tooth.has_appointment_treatments = Treatment.objects.filter(
            appointment=appointment, 
            tooth=tooth
        ).exists()
    
    context = {
        'appointment': appointment,
        'treatments': treatments,
        'status_choices': status_choices,
        'patient': patient,
        'recent_payments': recent_payments,
        'total_treatment_cost': total_treatment_cost,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'teeth': teeth,
    }
    return render(request, 'app/appointment_detail.html', context)

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            
            # Handle chief complaint
            chief_complaint = request.POST.get('chief_complaint', '')
            if chief_complaint:
                # Check if there's already a chief complaint in the notes
                if "Chief Complaint:" in updated_appointment.notes:
                    # Replace the existing chief complaint
                    notes_lines = updated_appointment.notes.split('\n')
                    new_notes = []
                    for line in notes_lines:
                        if line.strip().startswith("Chief Complaint:"):
                            new_notes.append(f"Chief Complaint: {chief_complaint}")
                        else:
                            new_notes.append(line)
                    updated_appointment.notes = '\n'.join(new_notes)
                else:
                    # Add chief complaint to notes
                    if updated_appointment.notes:
                        updated_appointment.notes += f"\n\nChief Complaint: {chief_complaint}"
                    else:
                        updated_appointment.notes = f"Chief Complaint: {chief_complaint}"
                
                # Also update patient's chief complaint if it's empty
                patient = updated_appointment.patient
                if not patient.chief_complaint or not patient.chief_complaint.strip():
                    patient.chief_complaint = chief_complaint
                    patient.save()
            
            updated_appointment.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        # Extract chief complaint from notes if it exists
        chief_complaint = ""
        if appointment.notes and "Chief Complaint:" in appointment.notes:
            for line in appointment.notes.split('\n'):
                if line.strip().startswith("Chief Complaint:"):
                    chief_complaint = line.replace("Chief Complaint:", "").strip()
                    break
        
        # Check if there are any URL parameters that should override the instance values
        patient_id = request.GET.get('patient')
        date_param = request.GET.get('date')
        dentist_id = request.GET.get('dentist')
        
        # Create initial data dictionary with instance values
        initial = {
            'patient': appointment.patient.id,
            'dentist': appointment.dentist.id,
            'date': appointment.date,
            'start_time': appointment.start_time,
            'notes': appointment.notes
        }
        
        # Override with URL parameters if present
        if patient_id:
            initial['patient'] = patient_id
        if date_param:
            try:
                # Try to parse the date parameter
                parsed_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                initial['date'] = parsed_date
            except ValueError:
                # Keep the original date if the format is invalid
                pass
        if dentist_id:
            initial['dentist'] = dentist_id
            
        form = AppointmentForm(instance=appointment, initial=initial)
    
    # Get all patients for the dropdown
    patients = Patient.objects.all().order_by('name')
    
    # Get all dentists for the dropdown
    dentists = User.objects.filter(profile__role='dentist')
    
    # Get available time slots for the selected date and dentist
    selected_date = request.GET.get('date', appointment.date.strftime('%Y-%m-%d'))
    selected_dentist_id = request.GET.get('dentist', str(appointment.dentist.id))
    
    # Generate time slots from 9 AM to 5 PM in 30-minute intervals
    time_slots = []
    start_hour = 9  # 9 AM
    end_hour = 17   # 5 PM
    
    current_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=start_hour)
    end_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=end_hour)
    
    while current_time < end_time:
        time_slot = {
            'time': current_time.time(),
            'display': current_time.strftime('%I:%M %p'),
            'available': True,
            'selected': False
        }
        
        # Check if this is the current appointment's time
        if current_time.time().strftime('%H:%M') == appointment.start_time.strftime('%H:%M'):
            time_slot['selected'] = True
            
        time_slots.append(time_slot)
        current_time += timedelta(minutes=30)
    
    # Mark booked slots as unavailable (except for this appointment's slot)
    if selected_date and selected_dentist_id:
        try:
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            booked_appointments = Appointment.objects.filter(
                dentist_id=selected_dentist_id,
                date=selected_date_obj,
                status='scheduled'
            ).exclude(pk=appointment.pk)  # Exclude current appointment
            
            for booked_appointment in booked_appointments:
                # Mark all slots that overlap with this appointment as unavailable
                for slot in time_slots:
                    slot_start = datetime.combine(selected_date_obj, slot['time'])
                    slot_end = slot_start + timedelta(minutes=30)
                    appointment_start = datetime.combine(selected_date_obj, booked_appointment.start_time)
                    appointment_end = datetime.combine(selected_date_obj, booked_appointment.end_time)
                    
                    if (slot_start < appointment_end and slot_end > appointment_start):
                        slot['available'] = False
        except (ValueError, TypeError):
            # Handle invalid date format
            pass
    
    context = {
        'form': form,
        'appointment': appointment,
        'patients': patients,
        'dentists': dentists,
        'time_slots': time_slots,
        'selected_date': selected_date,
        'selected_dentist_id': selected_dentist_id,
        'title': 'Update Appointment',
        'chief_complaint': chief_complaint,
    }
    return render(request, 'app/appointment_form.html', context)

@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
        return redirect('appointment_list')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'app/appointment_cancel.html', context)

@login_required
def appointment_status_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}!')
        else:
            messages.error(request, 'Invalid status provided!')
        return redirect('appointment_detail', pk=appointment.pk)
    
    context = {
        'appointment': appointment,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'app/appointment_status_update.html', context)

@login_required
def dental_chart(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get the appointment ID from query parameters if available
    appointment_id = request.GET.get('appointment')
    
    # Try to get the specific appointment first, then fall back to latest if not specified
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    else:
        # Get the latest appointment for this patient
        appointment = Appointment.objects.filter(
            patient=patient
        ).order_by('-date', '-start_time').first()
    
    # If no appointment exists, redirect to patient detail
    if not appointment:
        messages.warning(request, 'No appointment found for this patient.')
        return redirect('patient_detail', pk=patient_id)
    
    # Get all teeth
    teeth = Tooth.objects.all().order_by('quadrant', 'position')
    
    # Add treatment status properties to each tooth
    for tooth in teeth:
        # Filter treatments based on whether an appointment is selected
        tooth_treatments = Treatment.objects.filter(
            patient=patient, 
            tooth=tooth,
            appointment=appointment
        )
        
        # Add properties to tooth object
        tooth.has_treatments = tooth_treatments.exists()
        tooth.has_planned_treatments = tooth_treatments.filter(status='planned').exists()
        tooth.has_in_progress_treatments = tooth_treatments.filter(status='in_progress').exists()
        tooth.has_completed_treatments = tooth_treatments.filter(status='completed').exists()
        
        tooth.treatment_counts = {
            'total': tooth_treatments.count(),
            'planned': tooth_treatments.filter(status='planned').count(),
            'in_progress': tooth_treatments.filter(status='in_progress').count(),
            'completed': tooth_treatments.filter(status='completed').count(),
            'cancelled': tooth_treatments.filter(status='cancelled').count(),
        }
    
    # Get all tooth conditions for the dropdown
    conditions = ToothCondition.objects.all()
    
    # Get patient's appointments for the dropdown
    appointments = Appointment.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'teeth': teeth,
        'conditions': conditions,
        'appointments': appointments,
        'appointment': appointment,  # Add the current appointment to context
        'selected_appointment_id': str(appointment.id) if appointment else None,
    }
    
    return render(request, 'app/dental_chart.html', context)

@login_required
def add_treatment(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        # Get the comma-separated list of tooth IDs
        tooth_ids_str = request.POST.get('tooth_ids', '')
        
        if not tooth_ids_str:
            messages.error(request, 'No teeth selected for treatment')
            return redirect('dental_chart', patient_id=patient.id)
        
        # Split the string into a list of tooth IDs
        tooth_ids = [int(id) for id in tooth_ids_str.split(',') if id.strip()]
        
        # Get other form data
        condition_id = request.POST.get('condition')
        appointment_id = request.POST.get('appointment')
        description = request.POST.get('description')
        status = request.POST.get('status')
        cost = request.POST.get('cost')
        
        # Handle empty cost value
        try:
            cost = float(cost) if cost and cost.strip() else 0
        except ValueError:
            cost = 0
        
        # Get the related objects
        condition = get_object_or_404(ToothCondition, id=condition_id)
        appointment = None
        if appointment_id:
            appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Create a treatment for each selected tooth
        treatments_created = 0
        for tooth_id in tooth_ids:
            try:
                tooth = Tooth.objects.get(id=tooth_id)
                treatment = Treatment.objects.create(
                    patient=patient,
                    tooth=tooth,
                    condition=condition,
                    appointment=appointment,
                    description=description,
                    status=status,
                    cost=cost
                )
                
                # Create initial treatment history record
                TreatmentHistory.objects.create(
                    treatment=treatment,
                    previous_status=None,
                    new_status=status,
                    appointment=appointment,
                    dentist=request.user,
                    notes=f"Treatment created with status {dict(Treatment.STATUS_CHOICES).get(status)} by {request.user.get_full_name() or request.user.username}"
                )
                
                treatments_created += 1
            except Tooth.DoesNotExist:
                continue
        
        if treatments_created > 0:
            messages.success(request, f'Treatment added for {treatments_created} teeth')
        else:
            messages.error(request, 'No treatments were created')
        
        # Redirect to appointment detail if appointment was specified
        if appointment:
            return redirect('appointment_detail', pk=appointment.id)
        else:
            return redirect('dental_chart', patient_id=patient.id)
    
    # If not POST, redirect back to dental chart
    return redirect('dental_chart', patient_id=patient.id)

@login_required
def get_tooth_treatments(request, tooth_id):
    tooth = get_object_or_404(Tooth, number=tooth_id)
    
    # Get patient_id from query parameters if provided
    patient_id = request.GET.get('patient_id')
    
    if patient_id:
        # Get treatments for this tooth and patient
        treatments = Treatment.objects.filter(
            tooth=tooth,
            patient_id=patient_id
        ).order_by('-created_at')
    else:
        # Get all treatments for this tooth
        treatments = Treatment.objects.filter(tooth=tooth).order_by('-created_at')
    
    # Prepare treatment data
    treatment_data = []
    for treatment in treatments:
        # Get treatment history
        history = TreatmentHistory.objects.filter(treatment=treatment).order_by('-created_at')
        history_data = []
        
        for h in history:
            history_data.append({
                'date': h.created_at.strftime('%Y-%m-%d %H:%M'),
                'previous_status': h.previous_status,
                'previous_status_display': dict(Treatment.STATUS_CHOICES).get(h.previous_status, 'Unknown'),
                'new_status': h.new_status,
                'new_status_display': dict(Treatment.STATUS_CHOICES).get(h.new_status, 'Unknown'),
                'dentist': h.dentist.get_full_name() if h.dentist and h.dentist.get_full_name() else (h.dentist.username if h.dentist else 'Unknown'),
                'appointment_date': h.appointment.date.strftime('%Y-%m-%d') if h.appointment else None,
                'appointment_id': h.appointment.id if h.appointment else None,
                'notes': h.notes
            })
        
        treatment_data.append({
            'id': treatment.id,
            'condition_name': treatment.condition.name,
            'description': treatment.description,
            'status': treatment.status,
            'status_display': treatment.get_status_display(),
            'cost': float(treatment.cost),
            'created_at': treatment.created_at.strftime('%Y-%m-%d'),
            'appointment_date': treatment.appointment.date.strftime('%Y-%m-%d') if treatment.appointment else None,
            'appointment_id': treatment.appointment.id if treatment.appointment else None,
            'history': history_data
        })
    
    # Return JSON response
    return JsonResponse({
        'tooth_id': tooth_id,
        'tooth_name': tooth.name,
        'treatments': treatment_data
    })

@login_required
def treatment_detail(request, pk):
    treatment = get_object_or_404(Treatment, pk=pk)
    
    # Get treatment history
    treatment_history = TreatmentHistory.objects.filter(treatment=treatment).order_by('-created_at')
    
    context = {
        'treatment': treatment,
        'treatment_history': treatment_history,
        'referer': request.META.get('HTTP_REFERER', reverse('patient_detail', args=[treatment.patient.id]))
    }
    return render(request, 'app/treatment_detail.html', context)

@login_required
def treatment_update(request, pk):
    treatment = get_object_or_404(Treatment, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        description = request.POST.get('description')
        cost = request.POST.get('cost', 0)
        appointment_id = request.POST.get('appointment')
        
        # Handle empty cost value
        try:
            cost = float(cost) if cost and cost.strip() else treatment.cost
        except ValueError:
            cost = treatment.cost
        
        # Store the previous status for history logging
        previous_status = treatment.status
        
        # Update the treatment
        treatment.status = status
        treatment.description = description
        treatment.cost = cost
        
        # Get the current appointment ID from the request if it exists
        current_appointment_id = request.POST.get('current_appointment')
        current_appointment = None
        
        if current_appointment_id:
            try:
                current_appointment = Appointment.objects.get(pk=current_appointment_id)
                # Update the treatment's appointment to the current one when status changes
                if previous_status != status:
                    treatment.appointment = current_appointment
            except Appointment.DoesNotExist:
                pass
        # If no current appointment specified but appointment_id is provided, use that
        elif appointment_id:
            try:
                appointment = Appointment.objects.get(pk=appointment_id)
                treatment.appointment = appointment
            except Appointment.DoesNotExist:
                pass
        
        treatment.save()
        
        # Log the treatment history if status has changed
        if previous_status != status:
            # Get the dentist's full name
            dentist_name = request.user.get_full_name() if request.user.get_full_name() else request.user.username
            
            # Use the current appointment for the history record
            if not current_appointment:
                # Try to get the appointment ID from the referer URL
                referer = request.POST.get('referer', '')
                if 'appointment_detail' in referer:
                    try:
                        # Extract appointment ID from referer URL
                        appointment_id_match = re.search(r'/appointments/(\d+)/', referer)
                        if appointment_id_match:
                            appointment_id = appointment_id_match.group(1)
                            current_appointment = Appointment.objects.get(pk=appointment_id)
                    except (Appointment.DoesNotExist, Exception):
                        current_appointment = treatment.appointment
                else:
                    current_appointment = treatment.appointment
            
            TreatmentHistory.objects.create(
                treatment=treatment,
                previous_status=previous_status,
                new_status=status,
                appointment=current_appointment,
                dentist=request.user,
                notes=f"Status updated from {dict(Treatment.STATUS_CHOICES).get(previous_status)} to {dict(Treatment.STATUS_CHOICES).get(status)} by {dentist_name}"
            )
        
        messages.success(request, 'Treatment updated successfully')
        
        # Redirect based on where the user came from
        referer = request.POST.get('referer', '')
        if referer:
            return redirect(referer)
        elif treatment.appointment:
            return redirect('appointment_detail', pk=treatment.appointment.id)
        else:
            return redirect('patient_detail', pk=treatment.patient.id)
    
    # Get the referer URL for the cancel button
    referer = request.META.get('HTTP_REFERER', '')
    
    context = {
        'treatment': treatment,
        'patient': treatment.patient,
        'referer': referer,
    }
    return render(request, 'app/treatment_update.html', context)

# API Endpoints
@login_required
def get_patient_complaints(request, patient_id):
    """API endpoint to get previous chief complaints for a patient"""
    try:
        patient = Patient.objects.get(pk=patient_id)
        
        # Get all non-empty chief complaints for this patient
        complaints = []
        if patient.chief_complaint and patient.chief_complaint.strip():
            complaints.append(patient.chief_complaint)
            
        # Get chief complaints from previous appointments
        appointment_complaints = Appointment.objects.filter(
            patient=patient, 
            notes__icontains='chief complaint'
        ).values_list('notes', flat=True)
        
        for note in appointment_complaints:
            if note and note.strip():
                complaints.append(note)
        
        # Remove duplicates and limit to 5 most recent
        unique_complaints = list(dict.fromkeys(complaints))[:5]
        
        return JsonResponse({'complaints': unique_complaints})
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_time_slots(request):
    """API endpoint to get available time slots for a dentist on a specific date"""
    try:
        dentist_id = request.GET.get('dentist')
        date_str = request.GET.get('date')
        selected_time = request.GET.get('selected_time', '')
        
        if not dentist_id or not date_str:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
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
        
        # Mark booked slots as unavailable
        booked_appointments = Appointment.objects.filter(
            dentist_id=dentist_id,
            date=selected_date,
            status='scheduled'
        )
        
        # If we're editing an existing appointment, exclude it from the booked appointments
        appointment_id = request.GET.get('appointment_id')
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
        
        return JsonResponse({'time_slots': time_slots})
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dental_chart_view(request, patient_id, tooth=None):
    patient = get_object_or_404(Patient, id=patient_id)
    # Get the latest appointment for this patient
    appointment = patient.appointment_set.latest('appointment_date')
    
    context = {
        'patient': patient,
        'tooth': tooth,
        'appointment': appointment,  # Add appointment to context
        # ... other context data ...
    }
    return render(request, 'app/dental_chart.html', context)

# Payment Views
@login_required
def payment_list(request, patient_id):
    """View to list all payments for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
    
    # Calculate totals
    total_treatment_cost = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_treatment_cost - total_paid
    
    context = {
        'patient': patient,
        'payments': payments,
        'total_treatment_cost': total_treatment_cost,
        'total_paid': total_paid,
        'balance_due': balance_due,
    }
    return render(request, 'app/payment_list.html', context)

@login_required
def payment_create(request, patient_id, appointment_id=None):
    """View to create a new payment"""
    patient = get_object_or_404(Patient, id=patient_id)
    appointment = None
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, patient=patient, appointment=appointment)
        formset = PaymentItemFormSet(request.POST, instance=Payment())
        
        if form.is_valid() and formset.is_valid():
            # Save the payment
            payment = form.save(commit=False)
            payment.patient = patient
            payment.appointment = appointment
            payment.created_by = request.user
            payment.save()
            
            # Save the payment items
            formset.instance = payment
            formset.save()
            
            messages.success(request, 'Payment recorded successfully.')
            
            # Redirect based on where the payment was created from
            if appointment:
                return redirect('appointment_detail', pk=appointment.id)
            else:
                return redirect('patient_detail', pk=patient.id)
    else:
        form = PaymentForm(patient=patient, appointment=appointment)
        formset = PaymentItemFormSet(instance=Payment())
        
        # Pre-populate with treatments if coming from an appointment
        if appointment:
            treatments = Treatment.objects.filter(appointment=appointment)
            if treatments.exists():
                # Create initial data for the formset
                initial_data = []
                for treatment in treatments:
                    initial_data.append({
                        'description': f"{treatment.condition.name} - {treatment.description}",
                        'amount': treatment.cost,
                        'treatment': treatment,
                    })
                formset = PaymentItemFormSet(instance=Payment(), initial=initial_data)
    
    # Get treatments for this patient for the dropdown
    treatments = Treatment.objects.filter(patient=patient)
    
    context = {
        'form': form,
        'formset': formset,
        'patient': patient,
        'appointment': appointment,
        'treatments': treatments,
    }
    return render(request, 'app/payment_form.html', context)

@login_required
def payment_detail(request, payment_id):
    """View to show payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    payment_items = payment.items.all()
    
    context = {
        'payment': payment,
        'payment_items': payment_items,
    }
    return render(request, 'app/payment_detail.html', context)

@login_required
def get_patient_balance(request, patient_id):
    """API endpoint to get a patient's balance"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get payments for this patient
    payments = Payment.objects.filter(patient=patient)
    
    # Calculate totals
    total_treatment_cost = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_treatment_cost - total_paid
    
    data = {
        'total_treatment_cost': float(total_treatment_cost),
        'total_paid': float(total_paid),
        'balance_due': float(balance_due),
    }
    return JsonResponse(data)

@login_required
def payment_balance(request, patient_id):
    """View to create a payment for the outstanding balance"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get payments for this patient
    payments = Payment.objects.filter(patient=patient)
    
    # Calculate the outstanding balance
    total_amount_billed = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_amount_billed - total_paid
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, patient=patient)
        formset = PaymentItemFormSet(request.POST, instance=Payment())
        
        if form.is_valid() and formset.is_valid():
            # Save the payment
            payment = form.save(commit=False)
            payment.patient = patient
            payment.created_by = request.user
            
            # For balance payments, we want to set total_amount to 0 
            # and amount_paid to the actual payment amount
            if 'is_balance_payment' in request.POST and request.POST['is_balance_payment'] == 'true':
                payment.total_amount = 0
            
            payment.save()
            
            # Save the payment items
            formset.instance = payment
            formset.save()
            
            messages.success(request, 'Balance payment recorded successfully.')
            return redirect('patient_detail', pk=patient.id)
    else:
        # Pre-fill the form with the outstanding balance
        initial_data = {
            'total_amount': 0,  # For balance payments, set total_amount to 0
            'amount_paid': balance_due,  # The amount being paid towards the balance
        }
        form = PaymentForm(patient=patient, initial=initial_data)
        
        # Create a payment item for the balance payment
        item_initial = [{
            'description': 'Payment towards outstanding balance',
            'amount': balance_due,
        }]
        formset = PaymentItemFormSet(instance=Payment(), initial=item_initial)
    
    context = {
        'form': form,
        'formset': formset,
        'patient': patient,
        'balance_due': balance_due,
        'is_balance_payment': True,
    }
    return render(request, 'app/payment_form.html', context)
