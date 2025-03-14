# DentChartzz API Tests

This directory contains comprehensive tests for the DentChartzz API. The tests cover all major endpoints and functionality of the API, ensuring that the application works as expected.

## Test Structure

The test suite is organized by resource type:

- `test_auth.py`: Tests for authentication endpoints (login, logout, registration, token refresh)
- `test_clinics.py`: Tests for clinic management endpoints
- `test_patients.py`: Tests for patient-related endpoints
- `test_appointments.py`: Tests for appointment-related endpoints
- `test_treatments.py`: Tests for treatment-related endpoints
- `test_payments.py`: Tests for payment-related endpoints

Each test file contains a test class with fixtures for setting up test data and test methods for each endpoint or functionality.

## Test Fixtures

Common fixtures are defined in `conftest.py` and include:

- `api_client`: A Django REST Framework test client
- `user`: A regular user for testing
- `admin_user`: An admin user for testing
- `clinic`: A test clinic
- `clinic_membership`: A membership linking a user to a clinic
- `authenticated_client`: A client with authentication set up

Resource-specific fixtures are defined in their respective test files.

## Running Tests

To run all tests:

```bash
python -m pytest api/tests/
```

To run tests for a specific resource:

```bash
python -m pytest api/tests/test_auth.py
```

To run a specific test:

```bash
python -m pytest api/tests/test_auth.py::TestAuthentication::test_login
```

To run tests with verbose output:

```bash
python -m pytest api/tests/ -v
```

## Test Coverage

The test suite covers:

1. **Authentication**:
   - User registration
   - Login and token generation
   - Token refresh
   - Logout and token blacklisting
   - User info retrieval
   - Clinic selection
   - Password change

2. **Clinic Management**:
   - Listing clinics
   - Creating clinics
   - Retrieving clinic details
   - Updating clinics
   - Managing clinic members

3. **Patient Management**:
   - Listing patients
   - Creating patients
   - Retrieving patient details
   - Updating patients
   - Searching patients
   - Clinic isolation (patients from one clinic not accessible from another)

4. **Appointment Management**:
   - Listing appointments
   - Creating appointments
   - Retrieving appointment details
   - Updating appointments
   - Canceling appointments
   - Updating appointment status
   - Getting available time slots
   - Filtering appointments by various criteria

5. **Treatment Management**:
   - Listing treatments
   - Creating treatments
   - Retrieving treatment details
   - Updating treatments
   - Updating treatment status
   - Getting treatments by tooth
   - Listing teeth
   - Getting tooth details
   - Getting treatments for a tooth

6. **Payment Management**:
   - Listing payments
   - Creating payments with items
   - Retrieving payment details
   - Updating payments
   - Updating payment items
   - Getting patient balance
   - Getting patient payments

## Test Assertions

Each test includes assertions to verify:

1. Correct HTTP status codes
2. Correct response data structure
3. Correct data values
4. Database state after operations
5. Proper error handling
6. Clinic isolation (data from one clinic not accessible from another)

## Adding New Tests

When adding new endpoints or functionality, follow these guidelines:

1. Create fixtures for any new resources
2. Test all CRUD operations
3. Test filtering and search functionality
4. Test permissions and access control
5. Test error cases
6. Verify database state after operations
7. Ensure clinic isolation 