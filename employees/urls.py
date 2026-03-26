from django.urls import path
from . import views

urlpatterns = [
    path('employees/',                    views.employee_list_create, name='employee-list-create'),
    path('employees/<int:employee_id>/',  views.employee_detail,       name='employee-detail'),
    path('departments/',                  views.department_list,       name='department-list'),
    path('dashboard/',                    views.dashboard_summary,     name='dashboard-summary'),
]