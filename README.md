# Backend (Django)
The Django backend provides the server-side logic and database interactions for the application.

## Environment Setup

To set up the environment for this project, follow the steps below:

### 1. Install Python 3.x and pip.
### 2. Create a virtual environment for the project using virtualenv or venv. You can create a virtual environment named "envpuf" using the following command:

```sh
python -m venv env
```
### 3. Activate the virtual environment. On macOS and Linux, run the following command:

```sh
source env/bin/activate
```

### 4. Install the project dependencies using pip:

```sh
pip install -r requirements.txt
```

### 5. Run the Django development server:

```sh
python manage.py runserver
```

### 6. Starting Redis Server

```sh
redis-server
```

### 7. To start the Celery worker, run the following command in the project root directory:

```sh
celery -A pufBackend worker  -l info
```

### 8. Start Daphne
Daphne is an ASGI server used to run Django applications with asynchronous support. To start Daphne, run the following command in the project root directory:

```sh
daphne pufBackend.asgi:application --port 8089
```
