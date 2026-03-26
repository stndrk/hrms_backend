import datetime
from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name    = serializers.CharField(source='employee.full_name',   read_only=True)
    employee_id_code = serializers.CharField(source='employee.employee_id', read_only=True)
    department       = serializers.CharField(source='employee.department',  read_only=True)

    class Meta:
        model  = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_code', 'department',
            'date', 'status', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_date(self, value):
        if value > datetime.date.today():
            raise serializers.ValidationError('Cannot mark attendance for a future date.')
        return value

    def validate(self, data):
        employee = data.get('employee', getattr(self.instance, 'employee', None))
        date     = data.get('date',     getattr(self.instance, 'date',     None))
        if employee and date:
            qs = Attendance.objects.filter(employee=employee, date=date)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'date': f'Attendance for {employee.full_name} on {date} already recorded.'})
        return data