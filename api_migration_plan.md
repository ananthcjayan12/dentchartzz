# DentChartzz API Migration Plan

This document outlines the plan for migrating the DentChartzz monolithic application to a separate API-driven architecture with a Django backend and React/Next.js frontend. The new architecture will support multiple clinics, allowing the software to be sold as a SaaS solution.

## Multi-Clinic Architecture

To support multiple clinics, we'll implement the following changes:

1. **Clinic Model**: Add a new Clinic model that will serve as the top-level entity
2. **Tenant Isolation**: All data will be associated with a specific clinic
3. **Authentication**: Users will be associated with one or more clinics
4. **API Design**: All API endpoints will be clinic-aware

### Clinic Data Model

```
Clinic
├── name
├── address
├── contact_info
├── subscription_plan
├── subscription_status
├── created_at
├── updated_at
└── settings (JSON field for clinic-specific settings)
```

### User-Clinic Relationship

```
ClinicMembership
├── user (ForeignKey to User)
├── clinic (ForeignKey to Clinic)
├── role (admin, dentist, staff)
├── is_primary (boolean)
├── created_at
└── updated_at
```

## Project Structure

### Backend (Django)
```
dentchartzz-api/
├── core/                  # Django project settings
├── api/                   # New API app
│   ├── views/             # API views organized by resource
│   │   ├── clinics.py     # Clinic management
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── treatments.py
│   │   ├── payments.py
│   │   └── auth.py
│   ├── serializers/       # DRF serializers
│   │   ├── clinics.py     # Clinic serializers
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── treatments.py
│   │   └── payments.py
│   ├── urls.py            # API URL routing
│   ├── permissions.py     # Custom permissions
│   ├── pagination.py      # Pagination settings
│   ├── filters.py         # API filtering
│   ├── models/            # Models organized by domain
│   │   ├── clinics.py     # Clinic and ClinicMembership models
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── treatments.py
│   │   └── payments.py
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
│   │   ├── clinics/       # Clinic management components
│   │   ├── patients/
│   │   ├── appointments/
│   │   ├── treatments/
│   │   ├── payments/
│   │   └── common/
│   ├── pages/             # Page components
│   │   ├── clinics/       # Clinic management pages
│   │   ├── patients/
│   │   ├── appointments/
│   │   ├── treatments/
│   │   └── payments/
│   ├── services/          # API service layer
│   │   ├── api.js         # Base API configuration
│   │   ├── clinicService.js # Clinic management service
│   │   ├── patientService.js
│   │   ├── appointmentService.js
│   │   ├── treatmentService.js
│   │   └── paymentService.js
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── context/           # React context providers
│   │   ├── AuthContext.js
│   │   └── ClinicContext.js # Current clinic context
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

- [x] **1.2. Multi-Clinic Support**
  - [x] Create Clinic model
  - [x] Create ClinicMembership model
  - [x] Update existing models to reference Clinic
  - [x] Implement clinic-based filtering for all queries

- [x] **1.3. Models and Database**
  - [x] Create models matching the existing application
  - [x] Set up database connection
  - [x] Create migrations
  - [x] Migrate database

- [x] **1.4. Authentication**
  - [x] Implement JWT authentication
  - [x] Create login/logout endpoints
  - [x] Set up token refresh mechanism
  - [x] Implement clinic selection during login
  - [x] Configure permissions based on clinic roles

- [x] **1.5. API Serializers**
  - [x] Create serializers for Clinic model
  - [x] Create serializers for Patient model
  - [x] Create serializers for Appointment model
  - [x] Create serializers for Treatment model
  - [x] Create serializers for Payment model
  - [x] Create serializers for other models (Tooth, ToothCondition, etc.)

- [x] **1.6. API Views and Endpoints**
  - [x] **Clinic Endpoints**
    - [x] GET /api/v1/clinics/ - List clinics user has access to
    - [x] POST /api/v1/clinics/ - Create a new clinic
    - [x] GET /api/v1/clinics/{id}/ - Get clinic details
    - [x] PUT /api/v1/clinics/{id}/ - Update clinic
    - [x] GET /api/v1/clinics/{id}/members/ - List clinic members
    - [x] POST /api/v1/clinics/{id}/members/ - Add member to clinic
    
  - [x] **Patient Endpoints**
    - [x] GET /api/v1/clinics/{clinic_id}/patients/ - List all patients
    - [x] POST /api/v1/clinics/{clinic_id}/patients/ - Create a new patient
    - [x] GET /api/v1/clinics/{clinic_id}/patients/{id}/ - Get patient details
    - [x] PUT /api/v1/clinics/{clinic_id}/patients/{id}/ - Update patient
    - [x] GET /api/v1/clinics/{clinic_id}/patients/{id}/complaints/ - Get patient complaints
    - [x] GET /api/v1/clinics/{clinic_id}/patients/{id}/balance/ - Get patient balance
    - [x] GET /api/v1/clinics/{clinic_id}/patients/{id}/dental-chart/ - Get dental chart

  - [x] **Appointment Endpoints**
    - [x] GET /api/v1/clinics/{clinic_id}/appointments/ - List all appointments
    - [x] POST /api/v1/clinics/{clinic_id}/appointments/ - Create a new appointment
    - [x] GET /api/v1/clinics/{clinic_id}/appointments/{id}/ - Get appointment details
    - [x] PUT /api/v1/clinics/{clinic_id}/appointments/{id}/ - Update appointment
    - [x] POST /api/v1/clinics/{clinic_id}/appointments/{id}/cancel/ - Cancel appointment
    - [x] PUT /api/v1/clinics/{clinic_id}/appointments/{id}/status/ - Update appointment status
    - [x] GET /api/v1/clinics/{clinic_id}/time-slots/ - Get available time slots

  - [x] **Treatment Endpoints**
    - [x] GET /api/v1/clinics/{clinic_id}/treatments/ - List all treatments
    - [x] POST /api/v1/clinics/{clinic_id}/treatments/ - Create a new treatment
    - [x] GET /api/v1/clinics/{clinic_id}/treatments/{id}/ - Get treatment details
    - [x] PUT /api/v1/clinics/{clinic_id}/treatments/{id}/ - Update treatment
    - [x] GET /api/v1/clinics/{clinic_id}/teeth/{id}/treatments/ - Get treatments for a tooth

  - [x] **Payment Endpoints**
    - [x] GET /api/v1/clinics/{clinic_id}/payments/ - List all payments
    - [x] POST /api/v1/clinics/{clinic_id}/payments/ - Create a new payment
    - [x] GET /api/v1/clinics/{clinic_id}/payments/{id}/ - Get payment details
    - [x] GET /api/v1/clinics/{clinic_id}/patients/{id}/payments/ - Get payments for a patient

- [x] **1.7. Testing**
  - [x] Write tests for authentication and clinic selection
  - [x] Write tests for clinic management
  - [x] Write tests for patient endpoints
  - [x] Write tests for appointment endpoints
  - [x] Write tests for treatment endpoints
  - [x] Write tests for payment endpoints

- [x] **1.8. API Documentation**
  - [x] Set up Swagger/OpenAPI documentation
  - [x] Document all endpoints
  - [x] Create usage examples

### Phase 2: Frontend Development

- [ ] **2.1. Project Setup**
  - [ ] Create new Next.js project
  - [ ] Install required packages (axios, formik, yup, react-query, etc.)
  - [ ] Set up project structure
  - [ ] Configure environment variables

- [ ] **2.2. Authentication and Clinic Selection**
  - [ ] Create login page
  - [ ] Implement authentication service
  - [ ] Create clinic selection interface
  - [ ] Set up token storage and refresh
  - [ ] Create protected routes

- [ ] **2.3. Clinic Management**
  - [ ] Create clinic creation interface
  - [ ] Create clinic settings interface
  - [ ] Create user management interface
  - [ ] Implement clinic switching

- [ ] **2.4. API Service Layer**
  - [ ] Create base API configuration with clinic context
  - [ ] Implement clinic service
  - [ ] Implement patient service
  - [ ] Implement appointment service
  - [ ] Implement treatment service
  - [ ] Implement payment service

- [ ] **2.5. UI Components**
  - [ ] Create layout components with clinic context
  - [ ] Create clinic components
  - [ ] Create patient components
  - [ ] Create appointment components
  - [ ] Create treatment components
  - [ ] Create payment components
  - [ ] Create dental chart component

- [ ] **2.6. Pages**
  - [ ] Create dashboard page with clinic overview
  - [ ] Create clinic management pages
  - [ ] Create patient list and detail pages
  - [ ] Create appointment list and detail pages
  - [ ] Create treatment pages
  - [ ] Create payment pages

- [ ] **2.7. Testing**
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
  - [ ] Ensure proper clinic data isolation
  - [ ] Check for security vulnerabilities
  - [ ] Implement security best practices

### Phase 4: Deployment and Multi-Tenant Infrastructure

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

- [ ] **4.4. Multi-Tenant Management**
  - [ ] Implement subscription management
  - [ ] Set up usage monitoring
  - [ ] Create admin dashboard for tenant management

## Database Schema Changes

### New Models

#### Clinic
```python
class Clinic(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='basic')
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active')
    settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
```

#### ClinicMembership
```python
class ClinicMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('dentist', 'Dentist'),
        ('staff', 'Staff'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinic_memberships')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'clinic')
        
    def __str__(self):
        return f"{self.user.username} - {self.clinic.name} ({self.get_role_display()})"
```

### Modified Models

All existing models will need to be updated to include a reference to the Clinic model:

```python
class Patient(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patients')
    # ... existing fields
```

```python
class Appointment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    # ... existing fields
```

```python
class Treatment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatments')
    # ... existing fields
```

```python
class Payment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='payments')
    # ... existing fields
```

## API Implementation Examples

### Clinic ViewSet

```python
# api/views/clinics.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import Clinic, ClinicMembership
from api.serializers.clinics import ClinicSerializer, ClinicDetailSerializer, ClinicMembershipSerializer
from api.permissions import IsClinicAdmin

class ClinicViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return clinics the user is a member of
        return Clinic.objects.filter(memberships__user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClinicDetailSerializer
        return ClinicSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsClinicAdmin()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        clinic = self.get_object()
        memberships = ClinicMembership.objects.filter(clinic=clinic)
        serializer = ClinicMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        clinic = self.get_object()
        # Implementation for adding a member
        # ...
```

### Patient ViewSet with Clinic Filtering

```python
# api/views/patients.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from api.models import Patient, Payment, Clinic
from api.serializers.patients import PatientSerializer, PatientDetailSerializer

class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'phone', 'email']
    
    def get_queryset(self):
        # Get the clinic_id from the URL
        clinic_id = self.kwargs.get('clinic_id')
        
        # Filter patients by clinic
        return Patient.objects.filter(clinic_id=clinic_id)
    
    def perform_create(self, serializer):
        # Get the clinic_id from the URL
        clinic_id = self.kwargs.get('clinic_id')
        clinic = Clinic.objects.get(id=clinic_id)
        
        # Save with the clinic
        serializer.save(clinic=clinic)
    
    # ... rest of the implementation
```

## Frontend Implementation Examples

### Clinic Context

```javascript
// src/context/ClinicContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getClinics } from '../services/clinicService';

const ClinicContext = createContext();

export const ClinicProvider = ({ children }) => {
  const { user } = useAuth();
  const [clinics, setClinics] = useState([]);
  const [currentClinic, setCurrentClinic] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadClinics();
    } else {
      setClinics([]);
      setCurrentClinic(null);
      setLoading(false);
    }
  }, [user]);

  const loadClinics = async () => {
    try {
      setLoading(true);
      const response = await getClinics();
      setClinics(response.results);
      
      // Set current clinic from localStorage or use the first one
      const savedClinicId = localStorage.getItem('currentClinicId');
      if (savedClinicId && response.results.some(c => c.id === parseInt(savedClinicId))) {
        setCurrentClinic(response.results.find(c => c.id === parseInt(savedClinicId)));
      } else if (response.results.length > 0) {
        setCurrentClinic(response.results[0]);
        localStorage.setItem('currentClinicId', response.results[0].id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading clinics:', error);
      setLoading(false);
    }
  };

  const switchClinic = (clinicId) => {
    const clinic = clinics.find(c => c.id === clinicId);
    if (clinic) {
      setCurrentClinic(clinic);
      localStorage.setItem('currentClinicId', clinicId);
    }
  };

  return (
    <ClinicContext.Provider value={{ 
      clinics, 
      currentClinic, 
      loading, 
      switchClinic,
      refreshClinics: loadClinics
    }}>
      {children}
    </ClinicContext.Provider>
  );
};

export const useClinic = () => useContext(ClinicContext);
```

### API Service with Clinic Context

```javascript
// src/services/api.js
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // For session authentication
});

// Request interceptor for adding auth token and clinic context
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add clinic context to URL if needed
    const currentClinicId = localStorage.getItem('currentClinicId');
    if (currentClinicId && config.url && !config.url.includes('/clinics/') && !config.url.startsWith('/auth/')) {
      // Replace any existing clinic_id parameter
      const hasClinicParam = config.url.includes('clinic_id=');
      if (hasClinicParam) {
        config.url = config.url.replace(/clinic_id=\d+/, `clinic_id=${currentClinicId}`);
      } else {
        // Add clinic_id as query parameter
        const separator = config.url.includes('?') ? '&' : '?';
        config.url = `${config.url}${separator}clinic_id=${currentClinicId}`;
      }
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// ... rest of the implementation
```

## Additional Considerations

1. **Data Migration**: Plan for migrating existing data to the new multi-clinic structure.

2. **Subscription Management**: Implement a system for managing clinic subscriptions and billing.

3. **Clinic Onboarding**: Create a streamlined process for setting up new clinics.

4. **White Labeling**: Consider allowing clinics to customize the appearance of their instance.

5. **Data Isolation**: Ensure complete isolation of data between clinics for security and privacy.

6. **Performance**: Optimize database queries to handle multiple clinics efficiently.

7. **Reporting**: Implement clinic-specific reporting and analytics.

8. **Super Admin**: Create a super admin interface for managing all clinics. 