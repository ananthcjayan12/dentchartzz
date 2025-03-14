"""
Documentation for the DentChartzz API.

This module contains documentation for the API endpoints, including request and response examples.
"""

# Authentication endpoints
LOGIN_DOCS = {
    'operation_description': """
    Authenticate a user and return JWT tokens.
    
    This endpoint authenticates a user with their username and password and returns JWT access and refresh tokens.
    The access token is used for authenticating subsequent requests, while the refresh token is used to obtain a new access token when it expires.
    """,
    'responses': {
        200: {
            'description': 'User authenticated successfully',
            'example': {
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'clinics': [
                        {
                            'id': 1,
                            'name': 'Main Clinic',
                            'role': 'admin'
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Invalid credentials',
            'example': {
                'detail': 'No active account found with the given credentials'
            }
        }
    }
}

LOGOUT_DOCS = {
    'operation_description': """
    Logout a user by blacklisting their refresh token.
    
    This endpoint blacklists the user's refresh token, effectively logging them out.
    After calling this endpoint, the refresh token can no longer be used to obtain a new access token.
    """,
    'responses': {
        200: {
            'description': 'User logged out successfully',
            'example': {
                'detail': 'Logout successful'
            }
        },
        400: {
            'description': 'Invalid token',
            'example': {
                'detail': 'Token is invalid or expired'
            }
        }
    }
}

REGISTER_DOCS = {
    'operation_description': """
    Register a new user.
    
    This endpoint registers a new user with the provided information.
    After registration, the user can log in using their username and password.
    """,
    'responses': {
        201: {
            'description': 'User registered successfully',
            'example': {
                'id': 1,
                'username': 'johndoe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        },
        400: {
            'description': 'Invalid data',
            'example': {
                'username': ['This field is required.'],
                'password': ['This field is required.'],
                'email': ['Enter a valid email address.']
            }
        }
    }
}

# Clinic endpoints
CLINIC_LIST_DOCS = {
    'operation_description': """
    List all clinics the authenticated user has access to.
    
    This endpoint returns a list of clinics that the authenticated user is a member of.
    Each clinic includes basic information such as name, address, and the user's role in the clinic.
    """,
    'responses': {
        200: {
            'description': 'List of clinics',
            'example': {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'name': 'Main Clinic',
                        'address': '123 Main St',
                        'phone': '555-1234',
                        'email': 'info@mainclinic.com',
                        'user_role': 'admin'
                    },
                    {
                        'id': 2,
                        'name': 'Branch Clinic',
                        'address': '456 Branch St',
                        'phone': '555-5678',
                        'email': 'info@branchclinic.com',
                        'user_role': 'dentist'
                    }
                ]
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        }
    }
}

CLINIC_CREATE_DOCS = {
    'operation_description': """
    Create a new clinic.
    
    This endpoint creates a new clinic with the authenticated user as an admin.
    The user will automatically be added as a member of the clinic with the admin role.
    """,
    'responses': {
        201: {
            'description': 'Clinic created successfully',
            'example': {
                'id': 1,
                'name': 'New Clinic',
                'address': '789 New St',
                'phone': '555-9012',
                'email': 'info@newclinic.com',
                'settings': {},
                'user_role': 'admin'
            }
        },
        400: {
            'description': 'Invalid data',
            'example': {
                'name': ['This field is required.']
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        }
    }
}

# Patient endpoints
PATIENT_LIST_DOCS = {
    'operation_description': """
    List all patients in a clinic.
    
    This endpoint returns a list of patients in the specified clinic.
    The authenticated user must be a member of the clinic to access this endpoint.
    """,
    'responses': {
        200: {
            'description': 'List of patients',
            'example': {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'name': 'Jane Smith',
                        'age': 35,
                        'gender': 'F',
                        'phone': '555-1234',
                        'email': 'jane@example.com',
                        'address': '123 Main St'
                    },
                    {
                        'id': 2,
                        'name': 'John Doe',
                        'age': 42,
                        'gender': 'M',
                        'phone': '555-5678',
                        'email': 'john@example.com',
                        'address': '456 Oak St'
                    }
                ]
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        },
        403: {
            'description': 'Permission denied',
            'example': {
                'detail': 'You do not have permission to perform this action.'
            }
        },
        404: {
            'description': 'Clinic not found',
            'example': {
                'detail': 'Not found.'
            }
        }
    }
}

# Appointment endpoints
APPOINTMENT_LIST_DOCS = {
    'operation_description': """
    List all appointments in a clinic.
    
    This endpoint returns a list of appointments in the specified clinic.
    The authenticated user must be a member of the clinic to access this endpoint.
    """,
    'responses': {
        200: {
            'description': 'List of appointments',
            'example': {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'patient': {
                            'id': 1,
                            'name': 'Jane Smith'
                        },
                        'dentist': {
                            'id': 1,
                            'username': 'drdoe',
                            'first_name': 'John',
                            'last_name': 'Doe'
                        },
                        'date': '2023-04-15',
                        'start_time': '09:00:00',
                        'end_time': '09:30:00',
                        'status': 'scheduled',
                        'notes': 'Regular checkup'
                    },
                    {
                        'id': 2,
                        'patient': {
                            'id': 2,
                            'name': 'John Doe'
                        },
                        'dentist': {
                            'id': 1,
                            'username': 'drdoe',
                            'first_name': 'John',
                            'last_name': 'Doe'
                        },
                        'date': '2023-04-16',
                        'start_time': '10:00:00',
                        'end_time': '10:30:00',
                        'status': 'scheduled',
                        'notes': 'Tooth extraction'
                    }
                ]
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        },
        403: {
            'description': 'Permission denied',
            'example': {
                'detail': 'You do not have permission to perform this action.'
            }
        },
        404: {
            'description': 'Clinic not found',
            'example': {
                'detail': 'Not found.'
            }
        }
    }
}

# Treatment endpoints
TREATMENT_LIST_DOCS = {
    'operation_description': """
    List all treatments in a clinic.
    
    This endpoint returns a list of treatments in the specified clinic.
    The authenticated user must be a member of the clinic to access this endpoint.
    """,
    'responses': {
        200: {
            'description': 'List of treatments',
            'example': {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'patient': {
                            'id': 1,
                            'name': 'Jane Smith'
                        },
                        'tooth': {
                            'id': 11,
                            'number': 11,
                            'name': 'Upper Right Central Incisor'
                        },
                        'condition': {
                            'id': 1,
                            'name': 'Cavity'
                        },
                        'appointment': {
                            'id': 1,
                            'date': '2023-04-15'
                        },
                        'description': 'Filling needed',
                        'status': 'planned',
                        'cost': '100.00'
                    },
                    {
                        'id': 2,
                        'patient': {
                            'id': 2,
                            'name': 'John Doe'
                        },
                        'tooth': {
                            'id': 21,
                            'number': 21,
                            'name': 'Upper Left Central Incisor'
                        },
                        'condition': {
                            'id': 2,
                            'name': 'Root Canal'
                        },
                        'appointment': {
                            'id': 2,
                            'date': '2023-04-16'
                        },
                        'description': 'Root canal treatment',
                        'status': 'planned',
                        'cost': '200.00'
                    }
                ]
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        },
        403: {
            'description': 'Permission denied',
            'example': {
                'detail': 'You do not have permission to perform this action.'
            }
        },
        404: {
            'description': 'Clinic not found',
            'example': {
                'detail': 'Not found.'
            }
        }
    }
}

# Payment endpoints
PAYMENT_LIST_DOCS = {
    'operation_description': """
    List all payments in a clinic.
    
    This endpoint returns a list of payments in the specified clinic.
    The authenticated user must be a member of the clinic to access this endpoint.
    """,
    'responses': {
        200: {
            'description': 'List of payments',
            'example': {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'patient': {
                            'id': 1,
                            'name': 'Jane Smith'
                        },
                        'appointment': {
                            'id': 1,
                            'date': '2023-04-15'
                        },
                        'payment_date': '2023-04-15',
                        'total_amount': '100.00',
                        'amount_paid': '50.00',
                        'balance': '50.00',
                        'payment_method': 'cash',
                        'notes': 'Initial payment',
                        'items': [
                            {
                                'id': 1,
                                'description': 'Filling',
                                'amount': '100.00',
                                'treatment': 1
                            }
                        ]
                    },
                    {
                        'id': 2,
                        'patient': {
                            'id': 2,
                            'name': 'John Doe'
                        },
                        'appointment': {
                            'id': 2,
                            'date': '2023-04-16'
                        },
                        'payment_date': '2023-04-16',
                        'total_amount': '200.00',
                        'amount_paid': '200.00',
                        'balance': '0.00',
                        'payment_method': 'card',
                        'notes': 'Full payment',
                        'items': [
                            {
                                'id': 2,
                                'description': 'Root canal treatment',
                                'amount': '200.00',
                                'treatment': 2
                            }
                        ]
                    }
                ]
            }
        },
        401: {
            'description': 'Authentication credentials were not provided',
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        },
        403: {
            'description': 'Permission denied',
            'example': {
                'detail': 'You do not have permission to perform this action.'
            }
        },
        404: {
            'description': 'Clinic not found',
            'example': {
                'detail': 'Not found.'
            }
        }
    }
} 