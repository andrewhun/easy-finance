"""easy_finance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from background_task.models import Task
from finance.helpers import add_daily_entries_to_statements, add_weekly_entries_to_statements, add_monthly_entries_to_statements

urlpatterns = [
	path("", include("finance.urls")),
    path('admin/', admin.site.urls),
]

# clear the task to avoid duplication
Task.objects.all().delete()

# add tasks to the schedule
add_daily_entries_to_statements(repeat = Task.DAILY, repeat_until = None)
add_weekly_entries_to_statements(repeat = Task.WEEKLY, repeat_until = None)
add_monthly_entries_to_statements(repeat = Task.EVERY_4_WEEKS, repeat_until = None)