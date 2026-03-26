from django.db import models


class Department(models.TextChoices):
    ENGINEERING      = 'Engineering',       'Engineering'
    PRODUCT          = 'Product',           'Product'
    DESIGN           = 'Design',            'Design'
    MARKETING        = 'Marketing',         'Marketing'
    SALES            = 'Sales',             'Sales'
    HR               = 'HR',               'Human Resources'
    FINANCE          = 'Finance',           'Finance'
    OPERATIONS       = 'Operations',        'Operations'
    LEGAL            = 'Legal',             'Legal'
    CUSTOMER_SUPPORT = 'Customer Support',  'Customer Support'
    OTHER            = 'Other',             'Other'


class Employee(models.Model):
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique employee identifier, e.g. EMP-001',
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(
        unique=True,
        help_text='Work email address',
    )
    department = models.CharField(
        max_length=50,
        choices=Department.choices,
        default=Department.OTHER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f'{self.employee_id} – {self.full_name}'

    # ── Computed helpers (used by serializer as read-only fields) ──────────

    @property
    def total_present_days(self):
        return self.attendance_records.filter(status='Present').count()

    @property
    def total_absent_days(self):
        return self.attendance_records.filter(status='Absent').count()

    @property
    def total_attendance_records(self):
        return self.attendance_records.count()