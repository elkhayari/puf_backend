# Backend (Django)
The Django backend provides the server-side logic and database interactions for the application.

## Environment Setup

To set up the environment for this project, follow the steps below:

1. Install Python 3.x and pip.
2. Create a virtual environment for the project using virtualenv or venv. You can create a virtual environment named "envpuf" using the following command:

python -m venv env

3. Activate the virtual environment. On macOS and Linux, run the following command:

source env/bin/activate


4. Install the project dependencies using pip:

pip install -r requirements.txt

5. Run the Django development server:

python manage.py runserver

6. To start the Celery worker, run the following command in the project root directory:

celery -A pufBackend worker  -l info

7. Start Daphne
Daphne is an ASGI server used to run Django applications with asynchronous support. To start Daphne, run the following command in the project root directory:

daphne pufBackend.asgi:application --port 8089

## Project Structure
// TODO
