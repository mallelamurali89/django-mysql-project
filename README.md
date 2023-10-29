# Django Mysql Project with Docker

Installation

Follow these steps to set up the project locally:

1. Clone the Repository

        git clone https://github.com/mallelamurali89/django-mysql-project.git

    cd django-mysql-project

2. Create a Virtual Environment

    Create a virtual environment to isolate project dependencies:

        python -m venv venv

Activate the virtual environment:

    On Windows:
        . venv/Scripts/activate

    On macOS and Linux:
        source venv/bin/activate

Go to Project folder

    cd sna_project

3. Install Dependencies

    Install the required packages using pip:

        pip install -r requirements.txt

4. Configure Database

    Update your project's settings to configure the database (e.g., PostgreSQL, MySQL, SQLite) and other settings.

    # settings.py

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sna_db',
        'USER': 'root',
        'PASSWORD': '',
    }
}
5. Apply Migrations

    Apply the database migrations to create the necessary tables:

        python manage.py makemigrations

        python manage.py migrate

6. Create a Superuser (Admin User) (Optional)

    Create a superuser account to access the Django admin panel:

        python manage.py createsuperuser

7. Run the Development Server

    Start the Django development server:

        python manage.py runserver

Your project should now be running locally at http://localhost:8000/api/signup/.



