from django.db import models
from employees.models import Employee

class AttendanceStatus(models.TextChoices):
    PRESENT = 'Present', 'Present'
    ABSENT  = 'Absent',  'Absent'

class Attendance(models.Model):
    employee   = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date       = models.DateField()
    status     = models.CharField(max_length=10, choices=AttendanceStatus.choices, default='Present')
    notes      = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering        = ['-date', '-created_at']
        unique_together = [['employee', 'date']]

    def __str__(self):
        return f'{self.employee.employee_id} | {self.date} | {self.status}'