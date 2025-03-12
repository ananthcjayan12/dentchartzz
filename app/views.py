from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Patient, Appointment, Treatment, Tooth, ToothCondition, TreatmentHistory
from .forms import PatientForm, AppointmentForm, TreatmentForm
from datetime import date, datetime, timedelta
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

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
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    treatments = Treatment.objects.filter(patient=patient).order_by('-created_at')
    
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
    
    # Get treatments for this specific appointment
    appointment_treatments = Treatment.objects.filter(appointment=appointment)
    
    # Get all treatments for this patient
    all_patient_treatments = Treatment.objects.filter(patient=appointment.patient).order_by('-created_at')
    
    # Get all teeth for the dental chart
    teeth = Tooth.objects.all().order_by('quadrant', 'position')
    
    # Add treatment status properties to each tooth
    for tooth in teeth:
        # Get all treatments for this tooth from this patient
        tooth_treatments = Treatment.objects.filter(patient=appointment.patient, tooth=tooth)
        
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
        'appointment_treatments': appointment_treatments,
        'all_patient_treatments': all_patient_treatments,
        'teeth': teeth,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'app/appointment_detail.html', context)

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
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
    
    # Get all teeth
    teeth = Tooth.objects.all().order_by('quadrant', 'position')
    
    # Get pre-selected appointment from query parameters
    selected_appointment_id = request.GET.get('appointment')
    
    # Add treatment status properties to each tooth
    for tooth in teeth:
        # Filter treatments based on whether an appointment is selected
        if selected_appointment_id:
            tooth_treatments = Treatment.objects.filter(
                patient=patient, 
                tooth=tooth,
                appointment_id=selected_appointment_id
            )
        else:
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
    
    # Get all tooth conditions for the dropdown
    conditions = ToothCondition.objects.all()
    
    # Get patient's appointments for the dropdown
    appointments = Appointment.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'teeth': teeth,
        'conditions': conditions,
        'appointments': appointments,
        'selected_appointment_id': selected_appointment_id,
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
                Treatment.objects.create(
                    patient=patient,
                    tooth=tooth,
                    condition=condition,
                    appointment=appointment,
                    description=description,
                    status=status,
                    cost=cost
                )
                treatments_created += 1
            except Tooth.DoesNotExist:
                continue
        
        if treatments_created > 0:
            messages.success(request, f'Treatment added for {treatments_created} teeth')
        else:
            messages.error(request, 'No treatments were created')
        
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
        
        # Update the appointment if provided
        if appointment_id:
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
            
            TreatmentHistory.objects.create(
                treatment=treatment,
                previous_status=previous_status,
                new_status=status,
                appointment=treatment.appointment,
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
