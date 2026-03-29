# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active announcements on the homepage
- Manage announcements (signed-in users only)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| POST   | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Remove a student from an activity                               |
| POST   | `/auth/login?username=<username>&password=<password>`            | Login as a teacher/admin                                            |
| GET    | `/auth/check-session?username=<username>`                        | Validate a signed-in user session                                  |
| GET    | `/announcements`                                                  | Get active announcements (non-expired)                             |
| GET    | `/announcements?include_expired=true`                            | Get all announcements for management UI                             |
| POST   | `/announcements?message=<msg>&expiration_date=YYYY-MM-DD&teacher_username=<username>&start_date=YYYY-MM-DD(optional)` | Create announcement |
| PUT    | `/announcements/{announcement_id}?message=<msg>&expiration_date=YYYY-MM-DD&teacher_username=<username>&start_date=YYYY-MM-DD(optional)` | Update announcement |
| DELETE | `/announcements/{announcement_id}?teacher_username=<username>`    | Delete announcement                                                 |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Data is stored in MongoDB, and startup initialization in `backend/database.py` seeds sample activities, users, and an example announcement when collections are empty.
