# DentChartzz API Migration Plan

This document outlines the plan for migrating the DentChartzz monolithic application to a separate API-driven architecture with a Django backend and React/Next.js frontend.

## Project Structure

### Backend (Django)
```
dentchartzz-api/
├── core/                  # Django project settings
├── api/                   # New API app
│   ├── views/             # API views organized by resource
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── treatments.py
│   │   ├── payments.py
│   │   └── auth.py
│   ├── serializers/       # DRF serializers
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── treatments.py
│   │   └── payments.py
│   ├── urls.py            # API URL routing
│   ├── permissions.py     # Custom permissions
│   ├── pagination.py      # Pagination settings
│   ├── filters.py         # API filtering
│   ├── models.py          # Same models as the monolith
│   ├── apps.py
│   └── tests/             # API tests
├── manage.py
└── requirements.txt       # Including Django REST framework
```

### Frontend (React/Next.js)
```
dentchartzz-frontend/
├── public/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── layout/
│   │   ├── patients/
│   │   ├── appointments/
│   │   ├── treatments/
│   │   ├── payments/
│   │   └── common/
│   ├── pages/             # Page components
│   ├── services/          # API service layer
│   │   ├── api.js         # Base API configuration
│   │   ├── patientService.js
│   │   ├── appointmentService.js
│   │   ├── treatmentService.js
│   │   └── paymentService.js
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── context/           # React context providers
│   └── styles/            # CSS/SCSS styles
├── package.json
└── README.md
```

## Implementation Phases

### Phase 1: Backend API Development

- [x] **1.1. Project Setup**
  - [x] Create new Django project for the API
  - [x] Install required packages (Django REST Framework, CORS headers)
  - [x] Configure settings.py with DRF and CORS settings
  - [x] Set up project structure

- [ ] **1.2. Models and Database**
  - [ ] Create models matching the existing application
  - [ ] Set up database connection
  - [ ] Create migrations
  - [ ] Migrate database

- [ ] **1.3. Authentication**
  - [ ] Implement JWT authentication
  - [ ] Create login/logout endpoints
  - [ ] Set up token refresh mechanism
  - [ ] Configure permissions

- [ ] **1.4. API Serializers**
  - [ ] Create serializers for Patient model
  - [ ] Create serializers for Appointment model
  - [ ] Create serializers for Treatment model
  - [ ] Create serializers for Payment model
  - [ ] Create serializers for other models (Tooth, ToothCondition, etc.)

- [ ] **1.5. API Views and Endpoints**
  - [ ] **Patient Endpoints**
    - [ ] GET /api/v1/patients/ - List all patients
    - [ ] POST /api/v1/patients/ - Create a new patient
    - [ ] GET /api/v1/patients/{id}/ - Get patient details
    - [ ] PUT /api/v1/patients/{id}/ - Update patient
    - [ ] GET /api/v1/patients/{id}/complaints/ - Get patient complaints
    - [ ] GET /api/v1/patients/{id}/balance/ - Get patient balance
    - [ ] GET /api/v1/patients/{id}/dental-chart/ - Get dental chart

  - [ ] **Appointment Endpoints**
    - [ ] GET /api/v1/appointments/ - List all appointments
    - [ ] POST /api/v1/appointments/ - Create a new appointment
    - [ ] GET /api/v1/appointments/{id}/ - Get appointment details
    - [ ] PUT /api/v1/appointments/{id}/ - Update appointment
    - [ ] POST /api/v1/appointments/{id}/cancel/ - Cancel appointment
    - [ ] PUT /api/v1/appointments/{id}/status/ - Update appointment status
    - [ ] GET /api/v1/time-slots/ - Get available time slots

  - [ ] **Treatment Endpoints**
    - [ ] GET /api/v1/treatments/ - List all treatments
    - [ ] POST /api/v1/treatments/ - Create a new treatment
    - [ ] GET /api/v1/treatments/{id}/ - Get treatment details
    - [ ] PUT /api/v1/treatments/{id}/ - Update treatment
    - [ ] GET /api/v1/teeth/{id}/treatments/ - Get treatments for a tooth

  - [ ] **Payment Endpoints**
    - [ ] GET /api/v1/payments/ - List all payments
    - [ ] POST /api/v1/payments/ - Create a new payment
    - [ ] GET /api/v1/payments/{id}/ - Get payment details
    - [ ] GET /api/v1/patients/{id}/payments/ - Get payments for a patient

- [ ] **1.6. Testing**
  - [ ] Write tests for authentication
  - [ ] Write tests for patient endpoints
  - [ ] Write tests for appointment endpoints
  - [ ] Write tests for treatment endpoints
  - [ ] Write tests for payment endpoints

- [ ] **1.7. API Documentation**
  - [ ] Set up Swagger/OpenAPI documentation
  - [ ] Document all endpoints
  - [ ] Create usage examples

### Phase 2: Frontend Development

- [ ] **2.1. Project Setup**
  - [ ] Create new Next.js project
  - [ ] Install required packages (axios, formik, yup, react-query, etc.)
  - [ ] Set up project structure
  - [ ] Configure environment variables

- [ ] **2.2. Authentication**
  - [ ] Create login page
  - [ ] Implement authentication service
  - [ ] Set up token storage and refresh
  - [ ] Create protected routes

- [ ] **2.3. API Service Layer**
  - [ ] Create base API configuration
  - [ ] Implement patient service
  - [ ] Implement appointment service
  - [ ] Implement treatment service
  - [ ] Implement payment service

- [ ] **2.4. UI Components**
  - [ ] Create layout components
  - [ ] Create patient components
  - [ ] Create appointment components
  - [ ] Create treatment components
  - [ ] Create payment components
  - [ ] Create dental chart component

- [ ] **2.5. Pages**
  - [ ] Create dashboard page
  - [ ] Create patient list and detail pages
  - [ ] Create appointment list and detail pages
  - [ ] Create treatment pages
  - [ ] Create payment pages

- [ ] **2.6. Testing**
  - [ ] Write tests for components
  - [ ] Write tests for API services
  - [ ] Write end-to-end tests

### Phase 3: Integration and Testing

- [ ] **3.1. Integration**
  - [ ] Connect frontend to backend API
  - [ ] Test all functionality
  - [ ] Fix bugs and issues

- [ ] **3.2. Performance Optimization**
  - [ ] Optimize API responses
  - [ ] Implement caching
  - [ ] Optimize frontend performance

- [ ] **3.3. Security Review**
  - [ ] Review authentication and authorization
  - [ ] Check for security vulnerabilities
  - [ ] Implement security best practices

### Phase 4: Deployment

- [ ] **4.1. Backend Deployment**
  - [ ] Set up production environment
  - [ ] Configure CORS for production
  - [ ] Deploy backend API

- [ ] **4.2. Frontend Deployment**
  - [ ] Build production version
  - [ ] Deploy frontend application

- [ ] **4.3. CI/CD Setup**
  - [ ] Set up CI/CD pipeline
  - [ ] Configure automated testing
  - [ ] Configure automated deployment

## API Endpoints Mapping

| Current Endpoint | New API Endpoint | HTTP Method |
|------------------|------------------|-------------|
| `/patients/` | `/api/v1/patients/` | GET |
| `/patients/add/` | `/api/v1/patients/` | POST |
| `/patients/<id>/` | `/api/v1/patients/<id>/` | GET |
| `/patients/<id>/edit/` | `/api/v1/patients/<id>/` | PUT |
| `/appointments/` | `/api/v1/appointments/` | GET |
| `/appointments/add/` | `/api/v1/appointments/` | POST |
| `/appointments/<id>/` | `/api/v1/appointments/<id>/` | GET |
| `/appointments/<id>/edit/` | `/api/v1/appointments/<id>/` | PUT |
| `/appointments/<id>/cancel/` | `/api/v1/appointments/<id>/cancel/` | POST |
| `/appointments/<id>/status/` | `/api/v1/appointments/<id>/status/` | PUT |
| `/patients/<id>/dental-chart/` | `/api/v1/patients/<id>/dental-chart/` | GET |
| `/patients/<id>/add-treatment/` | `/api/v1/treatments/` | POST |
| `/treatments/tooth/<id>/` | `/api/v1/teeth/<id>/treatments/` | GET |
| `/treatments/<id>/` | `/api/v1/treatments/<id>/` | GET |
| `/treatments/<id>/update/` | `/api/v1/treatments/<id>/` | PUT |
| `/patients/<id>/payments/` | `/api/v1/patients/<id>/payments/` | GET |
| `/patients/<id>/payments/create/` | `/api/v1/payments/` | POST |
| `/patients/<id>/payments/balance/` | `/api/v1/patients/<id>/balance/` | GET |
| `/payments/<id>/` | `/api/v1/payments/<id>/` | GET |
| `/api/patients/<id>/balance/` | `/api/v1/patients/<id>/balance/` | GET |
| `/api/patient/<id>/complaints/` | `/api/v1/patients/<id>/complaints/` | GET |
| `/api/time-slots/` | `/api/v1/time-slots/` | GET |

## Implementation Examples

### Backend Example: Patient ViewSet

```python
# api/views/patients.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from api.models import Patient, Payment
from api.serializers.patients import PatientSerializer, PatientDetailSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'phone', 'email']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    @action(detail=True, methods=['get'])
    def complaints(self, request, pk=None):
        """Get previous chief complaints for a patient"""
        patient = self.get_object()
        
        # Get all non-empty chief complaints for this patient
        complaints = []
        if patient.chief_complaint and patient.chief_complaint.strip():
            complaints.append(patient.chief_complaint)
            
        # Get chief complaints from previous appointments
        appointment_complaints = patient.appointments.filter(
            notes__icontains='chief complaint'
        ).values_list('notes', flat=True)
        
        for note in appointment_complaints:
            if note and note.strip():
                complaints.append(note)
        
        # Remove duplicates and limit to 5 most recent
        unique_complaints = list(dict.fromkeys(complaints))[:5]
        
        return Response({'complaints': unique_complaints})
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get a patient's balance"""
        patient = self.get_object()
        
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
        return Response(data)
```

### Frontend Example: Patient Service

```javascript
// src/services/patientService.js
import api from './api';

export const getPatients = async (searchParams = {}) => {
  const response = await api.get('/patients/', { params: searchParams });
  return response.data;
};

export const getPatient = async (id) => {
  const response = await api.get(`/patients/${id}/`);
  return response.data;
};

export const createPatient = async (patientData) => {
  const response = await api.post('/patients/', patientData);
  return response.data;
};

export const updatePatient = async (id, patientData) => {
  const response = await api.put(`/patients/${id}/`, patientData);
  return response.data;
};

export const getPatientComplaints = async (id) => {
  const response = await api.get(`/patients/${id}/complaints/`);
  return response.data;
};

export const getPatientBalance = async (id) => {
  const response = await api.get(`/patients/${id}/balance/`);
  return response.data;
};
```

## Additional Considerations

1. **Authentication**: Use JWT for stateless authentication between frontend and backend.

2. **Data Validation**: Implement thorough validation in both frontend and backend.

3. **Error Handling**: Create consistent error responses and handle them properly in the frontend.

4. **Documentation**: Use tools like Swagger/OpenAPI to document the API.

5. **Testing**: Write comprehensive tests for both frontend and backend.

6. **Security**: Implement proper security measures (HTTPS, CSRF protection, input validation).

7. **Performance**: Optimize API responses with pagination, filtering, and caching.

8. **Monitoring**: Set up logging and monitoring for the API. 