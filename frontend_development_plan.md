# DentChartzz Frontend Development Plan with Next.js and Shadcn UI

## Step 1: Project Setup

1. **Create a new Next.js project**
   ```bash
   npx create-next-app@latest dentchartzz-frontend
   cd dentchartzz-frontend
   ```
   - Select the following options:
     - TypeScript: Yes
     - ESLint: Yes
     - Tailwind CSS: Yes
     - App Router: Yes
     - Import alias: Yes (use @/ as the default)

2. **Install Shadcn UI**
   ```bash
   npx shadcn-ui@latest init
   ```
   - Select the following options:
     - Style: Default (or choose your preferred style)
     - Base color: Slate (or choose your preferred color)
     - CSS variables: Yes
     - Global CSS: Yes
     - React Server Components: Yes
     - Tailwind CSS: Yes
     - Import alias: @/components

3. **Install required dependencies**
   ```bash
   npm install axios jwt-decode react-hook-form zod @hookform/resolvers/zod date-fns react-day-picker
   ```

4. **Set up environment variables**
   Create a `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://your-api-url/api/v1
   ```

## Step 2: Authentication Setup

1. **Create authentication context**
   Create `src/contexts/AuthContext.tsx`:
   ```tsx
   // Import necessary libraries and set up authentication context with JWT handling
   // Include login, logout, token refresh functions
   // Store user data and authentication state
   ```

2. **Install Shadcn UI components for authentication**
   ```bash
   npx shadcn-ui@latest add button card input form label toast
   ```

3. **Create login page**
   Create `app/(auth)/login/page.tsx`:
   - Implement login form with email/username and password
   - Handle form submission and API calls
   - Redirect to dashboard on successful login
   - Show error messages for failed login attempts

4. **Create authentication API service**
   Create `src/services/auth.service.ts`:
   - Implement login, logout, token refresh functions
   - Handle JWT storage and retrieval
   - Implement user profile fetching

## Step 3: Layout and Navigation

1. **Install Shadcn UI components for layout**
   ```bash
   npx shadcn-ui@latest add sheet avatar dropdown-menu separator scroll-area
   ```

2. **Create main layout**
   Create `app/(dashboard)/layout.tsx`:
   - Implement sidebar with navigation links
   - Create responsive header with user menu
   - Add clinic selector dropdown
   - Implement mobile-friendly navigation

3. **Create protected route middleware**
   Create `src/middleware.ts`:
   - Check for authentication on protected routes
   - Redirect to login if not authenticated
   - Handle token expiration and refresh

## Step 4: Dashboard Implementation

1. **Install Shadcn UI components for dashboard**
   ```bash
   npx shadcn-ui@latest add card tabs table badge hover-card
   ```

2. **Create dashboard page**
   Create `app/(dashboard)/dashboard/page.tsx`:
   - Implement statistics cards (patients, appointments, treatments)
   - Create today's appointments table
   - Add quick action buttons
   - Implement responsive layout

3. **Create dashboard API service**
   Create `src/services/dashboard.service.ts`:
   - Implement functions to fetch dashboard data
   - Handle API calls for statistics and appointments

## Step 5: Patients Management

1. **Install Shadcn UI components for patients**
   ```bash
   npx shadcn-ui@latest add data-table dialog command pagination
   ```

2. **Create patients list page**
   Create `app/(dashboard)/patients/page.tsx`:
   - Implement data table with pagination
   - Add search and filter functionality
   - Include quick actions (view, edit, delete)

3. **Create patient detail page**
   Create `app/(dashboard)/patients/[id]/page.tsx`:
   - Display patient information
   - Show treatment history
   - Display appointment history
   - Show payment history and balance

4. **Create patient form**
   Create `app/(dashboard)/patients/new/page.tsx` and `app/(dashboard)/patients/[id]/edit/page.tsx`:
   - Implement form with validation
   - Handle form submission
   - Show success/error messages

5. **Create patients API service**
   Create `src/services/patients.service.ts`:
   - Implement CRUD operations for patients
   - Handle API calls for patient data

## Step 6: Appointments Management

1. **Install Shadcn UI components for appointments**
   ```bash
   npx shadcn-ui@latest add calendar popover select checkbox
   ```

2. **Create appointments list page**
   Create `app/(dashboard)/appointments/page.tsx`:
   - Implement data table with pagination
   - Add search and filter functionality
   - Include quick actions (view, edit, cancel)

3. **Create appointment calendar view**
   Create `app/(dashboard)/appointments/calendar/page.tsx`:
   - Implement calendar view with appointments
   - Add ability to create appointments by clicking on time slots
   - Show appointment details on hover

4. **Create appointment detail page**
   Create `app/(dashboard)/appointments/[id]/page.tsx`:
   - Display appointment information
   - Show patient information
   - Allow status updates
   - Enable adding treatments

5. **Create appointment form**
   Create `app/(dashboard)/appointments/new/page.tsx` and `app/(dashboard)/appointments/[id]/edit/page.tsx`:
   - Implement form with validation
   - Add time slot selection
   - Include patient selection (with search)
   - Handle form submission

6. **Create appointments API service**
   Create `src/services/appointments.service.ts`:
   - Implement CRUD operations for appointments
   - Handle API calls for appointment data
   - Implement time slot fetching

## Step 7: Dental Chart Implementation

1. **Install Shadcn UI components for dental chart**
   ```bash
   npx shadcn-ui@latest add tooltip hover-card accordion tabs
   ```

2. **Create dental chart component**
   Create `src/components/dental-chart/DentalChart.tsx`:
   - Implement interactive dental chart
   - Add tooth selection functionality
   - Show treatment history for selected tooth
   - Enable adding treatments to teeth

3. **Create dental chart page**
   Create `app/(dashboard)/patients/[id]/dental-chart/page.tsx`:
   - Integrate dental chart component
   - Add treatment form
   - Show treatment history
   - Implement saving functionality

4. **Create dental chart API service**
   Create `src/services/dental-chart.service.ts`:
   - Implement functions to fetch dental chart data
   - Handle API calls for tooth treatments

## Step 8: Treatments Management

1. **Install Shadcn UI components for treatments**
   ```bash
   npx shadcn-ui@latest add combobox textarea switch
   ```

2. **Create treatment detail page**
   Create `app/(dashboard)/treatments/[id]/page.tsx`:
   - Display treatment information
   - Show patient information
   - Allow status updates
   - Enable adding notes

3. **Create treatment form**
   Create `app/(dashboard)/treatments/new/page.tsx` and `app/(dashboard)/treatments/[id]/edit/page.tsx`:
   - Implement form with validation
   - Add tooth selection
   - Include treatment type selection
   - Handle form submission

4. **Create treatments API service**
   Create `src/services/treatments.service.ts`:
   - Implement CRUD operations for treatments
   - Handle API calls for treatment data

## Step 9: Payments Management

1. **Install Shadcn UI components for payments**
   ```bash
   npx shadcn-ui@latest add card sheet dialog alert
   ```

2. **Create payments list page**
   Create `app/(dashboard)/payments/page.tsx`:
   - Implement data table with pagination
   - Add search and filter functionality
   - Include quick actions (view, edit)

3. **Create payment detail page**
   Create `app/(dashboard)/payments/[id]/page.tsx`:
   - Display payment information
   - Show patient information
   - Show related treatments

4. **Create payment form**
   Create `app/(dashboard)/payments/new/page.tsx` and `app/(dashboard)/payments/[id]/edit/page.tsx`:
   - Implement form with validation
   - Add patient selection
   - Include treatment selection
   - Handle form submission

5. **Create payments API service**
   Create `src/services/payments.service.ts`:
   - Implement CRUD operations for payments
   - Handle API calls for payment data

## Step 10: Multi-Clinic Support

1. **Create clinic selector component**
   Create `src/components/clinic/ClinicSelector.tsx`:
   - Implement dropdown for clinic selection
   - Handle clinic switching
   - Update context with selected clinic

2. **Update API services for multi-clinic support**
   - Modify all API services to include clinic ID in requests
   - Update authentication context to store user's clinics
   - Implement clinic selection persistence

## Step 11: Error Handling and Notifications

1. **Install Shadcn UI components for notifications**
   ```bash
   npx shadcn-ui@latest add toast alert-dialog
   ```

2. **Create error boundary component**
   Create `src/components/ErrorBoundary.tsx`:
   - Implement error catching
   - Display user-friendly error messages
   - Add retry functionality

3. **Create toast notification service**
   Create `src/services/toast.service.ts`:
   - Implement functions for showing success, error, and info messages
   - Add timeout and dismissal functionality

## Step 12: Testing and Optimization

1. **Set up testing environment**
   ```bash
   npm install --save-dev jest @testing-library/react @testing-library/jest-dom
   ```

2. **Create tests for components and pages**
   - Write unit tests for key components
   - Create integration tests for pages
   - Test authentication flow

3. **Optimize performance**
   - Implement code splitting
   - Add image optimization
   - Enable server-side rendering for key pages
   - Implement caching strategies

## Step 13: Deployment

1. **Prepare for production**
   ```bash
   npm run build
   ```

2. **Deploy to hosting platform**
   - Deploy to Vercel, Netlify, or your preferred hosting platform
   - Set up environment variables
   - Configure custom domain if needed

3. **Set up CI/CD pipeline**
   - Configure GitHub Actions or other CI/CD tool
   - Implement automated testing
   - Set up automatic deployment on merge to main branch

## Step 14: Documentation

1. **Create user documentation**
   - Write user guide for the application
   - Create help pages within the application
   - Add tooltips for complex features

2. **Create developer documentation**
   - Document code structure
   - Write API integration guide
   - Create component documentation

## API Integration

The frontend will integrate with the DentChartzz API as described in the API documentation. Key endpoints include:

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token

### Clinics
- `GET /api/v1/clinics/` - List clinics user has access to
- `POST /api/v1/clinics/` - Create a new clinic
- `GET /api/v1/clinics/{id}/` - Get clinic details

### Patients
- `GET /api/v1/clinics/{clinic_id}/patients/` - List all patients
- `POST /api/v1/clinics/{clinic_id}/patients/` - Create a new patient
- `GET /api/v1/clinics/{clinic_id}/patients/{id}/` - Get patient details

### Appointments
- `GET /api/v1/clinics/{clinic_id}/appointments/` - List all appointments
- `POST /api/v1/clinics/{clinic_id}/appointments/` - Create a new appointment
- `GET /api/v1/clinics/{clinic_id}/appointments/{id}/` - Get appointment details

### Treatments
- `GET /api/v1/clinics/{clinic_id}/treatments/` - List all treatments
- `POST /api/v1/clinics/{clinic_id}/treatments/` - Create a new treatment
- `GET /api/v1/clinics/{clinic_id}/treatments/{id}/` - Get treatment details

### Payments
- `GET /api/v1/clinics/{clinic_id}/payments/` - List all payments
- `POST /api/v1/clinics/{clinic_id}/payments/` - Create a new payment
- `GET /api/v1/clinics/{clinic_id}/payments/{id}/` - Get payment details

## UI Design Guidelines

1. **Color Scheme**
   - Primary: Indigo (#4f46e5)
   - Secondary: Slate (#64748b)
   - Accent: Emerald (#10b981)
   - Background: White (#ffffff) and Light Gray (#f9fafb)
   - Text: Dark Gray (#1f2937) and Medium Gray (#6b7280)

2. **Typography**
   - Font Family: Inter (sans-serif)
   - Headings: Semi-bold, sizes ranging from 1.125rem to 2.25rem
   - Body Text: Regular, 0.875rem to 1rem
   - Line Height: 1.5 to 1.75

3. **Component Styling**
   - Rounded corners (0.375rem to 0.5rem)
   - Subtle shadows for elevation
   - Consistent padding and spacing
   - Clear visual hierarchy
   - Responsive design for all screen sizes

4. **Accessibility**
   - Minimum contrast ratio of 4.5:1
   - Keyboard navigation support
   - Screen reader friendly
   - Focus indicators for interactive elements
   - Appropriate text alternatives for non-text content 