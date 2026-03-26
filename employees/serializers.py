import re
from rest_framework import serializers
from .models import Employee, Department


class EmployeeSerializer(serializers.ModelSerializer):
    total_present_days       = serializers.ReadOnlyField()
    total_absent_days        = serializers.ReadOnlyField()
    total_attendance_records = serializers.ReadOnlyField()

    class Meta:
        model  = Employee
        fields = [
            'id',
            'employee_id',
            'full_name',
            'email',
            'department',
            'created_at',
            'updated_at',
            'total_present_days',
            'total_absent_days',
            'total_attendance_records',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # ── Field-level validators ────────────────────────────────────────────

    def validate_employee_id(self, value):
        value = value.strip().upper()
        if not value:
            raise serializers.ValidationError('Employee ID cannot be blank.')
        if not re.match(r'^[A-Z0-9\-_]+$', value):
            raise serializers.ValidationError(
                'Employee ID may only contain letters, numbers, hyphens (-) or underscores (_).'
            )
        if len(value) > 20:
            raise serializers.ValidationError(
                'Employee ID must not exceed 20 characters.'
            )
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                'Full name must be at least 2 characters long.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Full name must not exceed 150 characters.'
            )
        if not re.match(r"^[A-Za-z\s'\-\.]+$", value):
            raise serializers.ValidationError(
                "Full name may only contain letters, spaces, apostrophes, hyphens, or dots."
            )
        return value

    def validate_email(self, value):
        return value.strip().lower()

    def validate_department(self, value):
        valid_values = [choice[0] for choice in Department.choices]
        if value not in valid_values:
            raise serializers.ValidationError(
                f'Invalid department. Valid options are: {", ".join(valid_values)}.'
            )
        return value

    # ── Object-level validator (uniqueness across fields) ─────────────────

    def validate(self, data):
        instance = self.instance   # None on create, Employee object on update

        emp_id = data.get('employee_id', getattr(instance, 'employee_id', None))
        email  = data.get('email',       getattr(instance, 'email',       None))

        # Uniqueness: employee_id
        qs_id = Employee.objects.filter(employee_id=emp_id)
        if instance:
            qs_id = qs_id.exclude(pk=instance.pk)
        if qs_id.exists():
            raise serializers.ValidationError(
                {'employee_id': 'An employee with this Employee ID already exists.'}
            )

        # Uniqueness: email
        qs_email = Employee.objects.filter(email=email)
        if instance:
            qs_email = qs_email.exclude(pk=instance.pk)
        if qs_email.exists():
            raise serializers.ValidationError(
                {'email': 'An employee with this email address already exists.'}
            )

        return data


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for the employee list endpoint.
    Includes only the fields the frontend table needs.
    """

    total_present_days = serializers.ReadOnlyField()

    class Meta:
        model  = Employee
        fields = [
            'id',
            'employee_id',
            'full_name',
            'email',
            'department',
            'created_at',
            'total_present_days',
        ]