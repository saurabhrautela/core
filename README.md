# core
Django application with user management to be used as base for different use cases.

## Instructions

### Setup development environment
1. Clone the repository: `git clone https://github.com/saurabhrautela/core.git`
2. Rename *config/server_config_reference.yml* to *config/server_config.yml*: `mv .\config\server_config_reference.yml .\config\server_config.yml`
3. Generate secret files: `cd .\config\secrets\ && .\bootstrap.sh`
4. Update files generated inside secrets folder with required values.
5. Update *.\config\server_config.yml* as needed.

### Start development server
1. (Optional) Start supporting services and software e.g. database, queue etc.: ``docker-compose -f local-docker-compose.yml up -d``
2. Create virtual environment and install dependencies: ``pipenv install --dev``
3. Activate virtual environment: ``pipenv shell``
4. Change directory to *dev*: ``cd dev``
5. Setup database schema: ``python manage.py makemigrations && python manage.py migrate``
6. Create superuser: ``python manage.py createsuperuser``
7. Start server: ``python manage.py runserver``

### Start development
1. Change directory to *dev*: ``cd dev``
2. Create app: ``python manage.py startapp app_name``
3. Register app in *dev/core/settings.py* file by adding it to ``INSTALLED_APPS`` array.
