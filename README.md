# Django REST API for Person Management

This Django project provides a RESTful API for managing persons in the system. It allows CRUD operations on person entities and provides filtering capabilities based on various parameters including first name, last name, and age.

## Features

- Standard REST CRUD operations for managing person entities.
- Ability to filter persons by first name, last name, and age.
- User-based authentication with support for admin and guest roles.
- Customized API error responses for better user experience.
- Self-describing API with Swagger documentation.

## Requirements

- Python 3.12
- Django 4.2
- Django REST Framework
- drf-yasg
## Installation


1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:

   ```bash
   python manage.py runserver
   ```

4. Access the API at `http://localhost:8000/`.

## Usage

- Access the API endpoints with browser or other tools such as curl and Postman.
- Swagger documentation is available at `doc/swagger/` and `doc/redoc/` for exploring the API endpoints and their parameters.


## API Endpoints

- `GET /person/`: Retrieve a list of all persons (admin only).
- `POST /person/`: Create a new person entity (admin only).
- `GET /person/<int:id>/`: Get the detail of a person entity (admin only).
- `PUT /person/<int:id>/`: Update a person entity (admin only).
- `PATCH /person/<int:id>/`: Partially update a person entity (admin only).
- `DELETE /person/<int:id>/`: Delete a person entity (admin only).
- `GET /filter-person/`: Retrieve a list of persons based on filters (admin and guest).
- `GET /filter-person/?first_name=<first_name>&last_name=<last_name>&min_age=<min_age>&max_age=<max_age>`: Filter persons by first name, last name, and age (admin and guest).

## Default Users

The API comes with two default users created for testing purposes:

1. **Guest User**
   - **Username:** alice
   - **Password:** alice123
   - **Role:** Guest
   
   The guest user has limited access to certain API endpoints and functionalities.

2. **Admin User**
   - **Username:** bob
   - **Password:** bob123
   - **Role:** Administrator
   
   The admin user has full access to all API endpoints and functionalities.

## Tests

The tests for the API can be found at `person/tests.py`.

To run the tests:
   ```bash
   python manage.py test
   ```