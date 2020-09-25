"""Register models to django admin."""
from django.contrib import admin
from users.models import User

admin.site.register(User)
