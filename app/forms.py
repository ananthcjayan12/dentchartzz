from django import forms
from django.forms import inlineformset_factory
from .models import Patient, Appointment, Treatment, Payment, PaymentItem

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'name', 'age', 'gender', 'date_of_birth', 'phone', 
            'email', 'address', 'chief_complaint', 'medical_history',
            'drug_allergies', 'previous_dental_work'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'drug_allergies': forms.Textarea(attrs={'rows': 3}),
            'previous_dental_work': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'chief_complaint': forms.Textarea(attrs={'rows': 3}),
        }

class AppointmentForm(forms.ModelForm):
    # Add a duration field (in minutes)
    duration = forms.IntegerField(
        initial=30,
        min_value=15,
        max_value=240,
        help_text="Duration in minutes",
        widget=forms.NumberInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'})
    )
    
    # Add chief complaint field
    chief_complaint = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Enter patient\'s main dental concern or reason for visit'
        })
    )
    
    class Meta:
        model = Appointment
        fields = ['patient', 'dentist', 'date', 'start_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        date = cleaned_data.get('date')
        dentist = cleaned_data.get('dentist')
        duration = cleaned_data.get('duration', 30)  # Default to 30 minutes

        if start_time and date and dentist:
            # Calculate end_time based on start_time and duration
            from datetime import datetime, timedelta
            
            # Create a datetime object to perform the calculation
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Extract the time component
            end_time = end_datetime.time()
            
            # Add end_time to cleaned_data
            cleaned_data['end_time'] = end_time
            
            # Check for overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                dentist=dentist,
                date=date,
                status='scheduled'
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for appointment in overlapping_appointments:
                # Check if the new appointment overlaps with existing ones
                if (start_time < appointment.end_time and end_time > appointment.start_time):
                    self.add_error(None, f"This appointment overlaps with another appointment for {dentist.get_full_name()} on {date} at {appointment.start_time.strftime('%I:%M %p')}.")
                    break
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculate end_time based on start_time and duration
        if instance.start_time and 'duration' in self.cleaned_data:
            from datetime import datetime, timedelta
            
            # Create a datetime object to perform the calculation
            start_datetime = datetime.combine(datetime.today(), instance.start_time)
            end_datetime = start_datetime + timedelta(minutes=self.cleaned_data['duration'])
            
            # Extract the time component
            instance.end_time = end_datetime.time()
        
        if commit:
            instance.save()
        
        return instance 

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['tooth', 'condition', 'appointment', 'description', 'status', 'cost']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        
        if patient:
            # Filter appointments to only show those for this patient
            self.fields['appointment'].queryset = Appointment.objects.filter(patient=patient)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_date', 'payment_method', 'total_amount', 'amount_paid', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly', 'id': 'id_total_amount'}),
        }
    
    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        appointment = kwargs.pop('appointment', None)
        super().__init__(*args, **kwargs)
        
        # Add data-* attributes for JavaScript functionality
        self.fields['amount_paid'].widget.attrs.update({'id': 'id_amount_paid'})
        
        # If this is a new payment, initialize with default values
        if not self.instance.pk:
            # Calculate total treatment cost for the patient
            from django.db.models import Sum
            if patient:
                total_cost = Treatment.objects.filter(patient=patient).aggregate(Sum('cost'))['cost__sum'] or 0
                total_paid = Payment.objects.filter(patient=patient).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
                self.fields['total_amount'].initial = total_cost - total_paid

# Create a formset for PaymentItems
PaymentItemFormSet = inlineformset_factory(
    Payment, 
    PaymentItem, 
    fields=('description', 'amount', 'treatment'),
    extra=1,
    can_delete=True,
    widgets={
        'description': forms.TextInput(attrs={'class': 'form-control'}),
        'amount': forms.NumberInput(attrs={'class': 'form-control payment-item-amount', 'step': '0.01'}),
    }
) 