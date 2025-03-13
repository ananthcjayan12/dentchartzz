# DentChartzz - Dental Clinic Management System

DentChartzz is a comprehensive dental clinic management system built with Django. It helps dental clinics manage patients, appointments, treatments, and dental charts.

## Features

- User management with different roles (admin, dentist, staff)
- Patient management
- Appointment scheduling and management
- Dental chart visualization
- Treatment planning and tracking
- Treatment history

## Dockerized Setup

This application is fully dockerized with PostgreSQL for better database management and persistence.

### Prerequisites

- Docker
- Docker Compose

### Development Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd dentchartzz
   ```

2. Run the development script:
   ```
   ./dev.sh
   ```

3. The application will be available at http://localhost:8000

### Production Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd dentchartzz
   ```

2. Run the production script:
   ```
   ./prod.sh
   ```

3. The application will be available at http://your-server-ip:8000

### Deployment to Coolify

1. Push your code to a Git repository
2. In Coolify, create a new service and select your repository
3. Choose "Docker Compose" as the deployment method
4. Select `docker-compose.prod.yml` as the Docker Compose file
5. Configure environment variables if needed
6. Deploy the application

### Default Users

The application comes with pre-configured users:

- Admin:
  - Username: admin
  - Password: admin123

- Dentist:
  - Username: dentist
  - Password: dentist123

- Staff:
  - Username: staff
  - Password: staff123

### Database Persistence

The PostgreSQL database is configured to persist data using Docker volumes. The data will be preserved even if you stop or restart the containers.

## Development

### Running Tests

To run the tests inside the Docker container:

```
docker-compose exec web python -m pytest
```

### Accessing the Database

You can access the PostgreSQL database directly using:

```
docker-compose exec db psql -U dentchartzz -d dentchartzz_db
```

## Stopping the Application

To stop the application:

```
docker-compose down
```

To stop the production application:

```
docker-compose -f docker-compose.prod.yml down
```

To stop the application and remove all data (including the database):

```
docker-compose down -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 