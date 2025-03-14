# DentChartzz API

The DentChartzz API is a RESTful API for managing dental clinics. It provides endpoints for managing clinics, patients, appointments, treatments, and payments.

## API Documentation

The API documentation is available at the following endpoints:

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI Schema: `/swagger.json` or `/swagger.yaml`

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate, send a POST request to `/api/v1/auth/login/` with your username and password. The response will include access and refresh tokens, which you can use to authenticate subsequent requests.

Example:

```json
// Request
POST /api/v1/auth/login/
{
  "username": "johndoe",
  "password": "password123"
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "clinics": [
      {
        "id": 1,
        "name": "Main Clinic",
        "role": "admin"
      }
    ]
  }
}
```

To authenticate requests, include the access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

Access tokens expire after a certain period. To get a new access token, send a POST request to `/api/v1/auth/token/refresh/` with your refresh token:

```json
// Request
POST /api/v1/auth/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

To log out, send a POST request to `/api/v1/auth/logout/` with your refresh token:

```json
// Request
POST /api/v1/auth/logout/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

// Response
{
  "detail": "Logout successful"
}
```

## Multi-Clinic Support

The API supports multiple clinics, allowing users to be members of multiple clinics with different roles. When making requests to clinic-specific endpoints, include the clinic ID in the URL:

```
GET /api/v1/clinics/{clinic_id}/patients/
```

## API Endpoints

The API provides the following endpoints:

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/register/` - User registration
- `GET /api/v1/auth/user/` - Get user info
- `POST /api/v1/auth/select-clinic/` - Select a clinic
- `POST /api/v1/auth/change-password/` - Change password

### Clinics
- `GET /api/v1/clinics/` - List clinics user has access to
- `POST /api/v1/clinics/` - Create a new clinic
- `GET /api/v1/clinics/{id}/` - Get clinic details
- `PUT /api/v1/clinics/{id}/` - Update clinic
- `GET /api/v1/clinics/{id}/members/` - List clinic members
- `POST /api/v1/clinics/{id}/members/` - Add member to clinic

### Patients
- `GET /api/v1/clinics/{clinic_id}/patients/` - List all patients
- `POST /api/v1/clinics/{clinic_id}/patients/` - Create a new patient
- `GET /api/v1/clinics/{clinic_id}/patients/{id}/` - Get patient details
- `PUT /api/v1/clinics/{clinic_id}/patients/{id}/` - Update patient
- `GET /api/v1/clinics/{clinic_id}/patients/{id}/complaints/` - Get patient complaints
- `GET /api/v1/clinics/{clinic_id}/patients/{id}/balance/` - Get patient balance
- `GET /api/v1/clinics/{clinic_id}/patients/{id}/dental-chart/` - Get dental chart

### Appointments
- `GET /api/v1/clinics/{clinic_id}/appointments/` - List all appointments
- `POST /api/v1/clinics/{clinic_id}/appointments/` - Create a new appointment
- `GET /api/v1/clinics/{clinic_id}/appointments/{id}/` - Get appointment details
- `PUT /api/v1/clinics/{clinic_id}/appointments/{id}/` - Update appointment
- `POST /api/v1/clinics/{clinic_id}/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/v1/clinics/{clinic_id}/appointments/{id}/status/` - Update appointment status
- `GET /api/v1/clinics/{clinic_id}/time-slots/` - Get available time slots

### Treatments
- `GET /api/v1/clinics/{clinic_id}/treatments/` - List all treatments
- `POST /api/v1/clinics/{clinic_id}/treatments/` - Create a new treatment
- `GET /api/v1/clinics/{clinic_id}/treatments/{id}/` - Get treatment details
- `PUT /api/v1/clinics/{clinic_id}/treatments/{id}/` - Update treatment
- `POST /api/v1/clinics/{clinic_id}/treatments/{id}/status/` - Update treatment status
- `GET /api/v1/clinics/{clinic_id}/treatments/by-tooth/` - Get treatments for a specific tooth
- `GET /api/v1/clinics/{clinic_id}/teeth/` - List all teeth
- `GET /api/v1/clinics/{clinic_id}/teeth/{id}/` - Get tooth details
- `GET /api/v1/clinics/{clinic_id}/teeth/{id}/treatments/` - Get treatments for a tooth

### Payments
- `GET /api/v1/clinics/{clinic_id}/payments/` - List all payments
- `POST /api/v1/clinics/{clinic_id}/payments/` - Create a new payment
- `GET /api/v1/clinics/{clinic_id}/payments/{id}/` - Get payment details
- `PUT /api/v1/clinics/{clinic_id}/payments/{id}/` - Update payment
- `GET /api/v1/clinics/{clinic_id}/payments/patient-balance/` - Get patient balance
- `GET /api/v1/clinics/{clinic_id}/payments/patient-payments/` - Get payments for a patient

## Error Handling

The API returns appropriate HTTP status codes and error messages for different types of errors:

- `400 Bad Request` - The request was invalid or cannot be served
- `401 Unauthorized` - Authentication credentials were not provided or are invalid
- `403 Forbidden` - The authenticated user does not have permission to access the requested resource
- `404 Not Found` - The requested resource does not exist
- `500 Internal Server Error` - An error occurred on the server

Error responses include a detail message explaining the error:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Pagination

List endpoints return paginated results. The response includes `count`, `next`, and `previous` fields, along with the `results` array:

```json
{
  "count": 100,
  "next": "http://example.com/api/v1/clinics/1/patients/?page=2",
  "previous": null,
  "results": [
    // ... items
  ]
}
```

## Filtering and Searching

Many list endpoints support filtering and searching. For example, to search for patients by name:

```
GET /api/v1/clinics/1/patients/?search=john
```

To filter appointments by date range:

```
GET /api/v1/clinics/1/appointments/?start_date=2023-04-01&end_date=2023-04-30
```

## Rate Limiting

The API implements rate limiting to prevent abuse. If you exceed the rate limit, you will receive a `429 Too Many Requests` response with a `Retry-After` header indicating how long to wait before making another request.

## Versioning

The API is versioned using URL path versioning. The current version is v1, which is included in the URL path:

```
/api/v1/
```

Future versions will be available at `/api/v2/`, `/api/v3/`, etc. 