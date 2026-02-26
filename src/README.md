# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active school announcements
- Signed-in teachers can create, edit, and delete announcements

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
| POST   | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity (requires auth)              |
| GET    | `/announcements`                                                  | Get active announcements (for banner display)                       |
| GET    | `/announcements/manage?teacher_username=username`                 | Get all announcements for management (requires auth)                |
| POST   | `/announcements?teacher_username=username`                        | Create an announcement (requires auth)                              |
| PUT    | `/announcements/{announcement_id}?teacher_username=username`      | Update an announcement (requires auth)                              |
| DELETE | `/announcements/{announcement_id}?teacher_username=username`      | Delete an announcement (requires auth)                              |

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

Data is stored in MongoDB collections. Initial example records are seeded by `database.py` when collections are empty.
