from django.urls import path
from . import views

urlpatterns = [
    path('attendance/',                          views.attendance_list_create, name='attendance-list-create'),
    path('attendance/<int:record_id>/',          views.attendance_detail,       name='attendance-detail'),
    path('employees/<int:employee_id>/attendance/', views.employee_attendance, name='employee-attendance'),
]