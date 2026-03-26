import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee

def ok(data, message='Success', code=status.HTTP_200_OK):
    return Response({'success': True, 'message': message, 'data': data}, status=code)

def fail(message, details=None, code=status.HTTP_400_BAD_REQUEST):
    body = {'success': False, 'message': message}
    if details:
        body['details'] = details
    return Response(body, status=code)


# GET /api/attendance/  POST /api/attendance/
@api_view(['GET', 'POST'])
def attendance_list_create(request):
    if request.method == 'GET':
        qs = Attendance.objects.select_related('employee').all()

        emp_id      = request.query_params.get('employee_id')
        date        = request.query_params.get('date')
        date_from   = request.query_params.get('date_from')
        date_to     = request.query_params.get('date_to')
        att_status  = request.query_params.get('status')
        department  = request.query_params.get('department')

        if emp_id:     qs = qs.filter(employee__id=emp_id)
        if date:       qs = qs.filter(date=date)
        if date_from:  qs = qs.filter(date__gte=date_from)
        if date_to:    qs = qs.filter(date__lte=date_to)
        if att_status: qs = qs.filter(status=att_status)
        if department: qs = qs.filter(employee__department=department)

        return ok({
            'records':       AttendanceSerializer(qs, many=True).data,
            'count':         qs.count(),
            'present_count': qs.filter(status='Present').count(),
            'absent_count':  qs.filter(status='Absent').count(),
        })

    # POST
    s = AttendanceSerializer(data=request.data)
    if s.is_valid():
        record = s.save()
        return ok(AttendanceSerializer(record).data, 'Attendance marked successfully.', status.HTTP_201_CREATED)
    return fail('Failed to mark attendance.', s.errors)


# GET PUT DELETE /api/attendance/<id>/
@api_view(['GET', 'PUT', 'DELETE'])
def attendance_detail(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)

    if request.method == 'GET':
        return ok(AttendanceSerializer(record).data)

    if request.method == 'PUT':
        s = AttendanceSerializer(record, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return ok(s.data, 'Attendance record updated.')
        return fail('Validation failed.', s.errors)

    record.delete()
    return ok(None, 'Attendance record deleted.')


# GET /api/employees/<employee_id>/attendance/
@api_view(['GET'])
def employee_attendance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    qs = Attendance.objects.filter(employee=employee).order_by('-date')

    date_from  = request.query_params.get('date_from')
    date_to    = request.query_params.get('date_to')
    att_status = request.query_params.get('status')

    if date_from:  qs = qs.filter(date__gte=date_from)
    if date_to:    qs = qs.filter(date__lte=date_to)
    if att_status: qs = qs.filter(status=att_status)

    return ok({
        'employee': {
            'id': employee.id, 'employee_id': employee.employee_id,
            'full_name': employee.full_name, 'department': employee.department,
            'email': employee.email,
        },
        'records':       AttendanceSerializer(qs, many=True).data,
        'count':         qs.count(),
        'present_count': qs.filter(status='Present').count(),
        'absent_count':  qs.filter(status='Absent').count(),
    })