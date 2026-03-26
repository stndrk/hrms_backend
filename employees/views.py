import datetime
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Employee, Department
from .serializers import EmployeeSerializer, EmployeeListSerializer


# ── Helpers ───────────────────────────────────────────────────────────────────

def ok(data, message='Success', http_status=status.HTTP_200_OK):
    """Standard success envelope matching the frontend expectations."""
    return Response(
        {'success': True, 'message': message, 'data': data},
        status=http_status,
    )


def err(message, details=None, http_status=status.HTTP_400_BAD_REQUEST):
    """Standard error envelope."""
    payload = {'success': False, 'message': message}
    if details:
        payload['details'] = details
    return Response(payload, status=http_status)


# ── Employee list + create ─────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def employee_list_create(request):
    """
    GET  /api/employees/
      Query params:
        search     – filters full_name, employee_id, email (case-insensitive)
        department – exact match on department field

    POST /api/employees/
      Body: { employee_id, full_name, email, department }
    """

    if request.method == 'GET':
        qs = Employee.objects.all()

        search     = request.query_params.get('search', '').strip()
        department = request.query_params.get('department', '').strip()

        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)   |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        if department:
            qs = qs.filter(department=department)

        serializer = EmployeeListSerializer(qs, many=True)
        return ok({
            'employees': serializer.data,
            'count':     qs.count(),
        })

    # ── POST ──────────────────────────────────────────────────────────────
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save()
        return ok(
            data        = EmployeeSerializer(employee).data,
            message     = 'Employee created successfully.',
            http_status = status.HTTP_201_CREATED,
        )

    return err(
        message     = 'Validation failed. Please check the submitted data.',
        details     = serializer.errors,
        http_status = status.HTTP_400_BAD_REQUEST,
    )


# ── Employee detail / update / delete ─────────────────────────────────────────

@api_view(['GET', 'PUT', 'DELETE'])
def employee_detail(request, employee_id):
    """
    GET    /api/employees/<employee_id>/   retrieve
    PUT    /api/employees/<employee_id>/   update (partial allowed)
    DELETE /api/employees/<employee_id>/   delete (cascades attendance records)
    """
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return ok(serializer.data)

    if request.method == 'PUT':
        # partial=True allows sending only the fields you want to change
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ok(
                data    = serializer.data,
                message = 'Employee updated successfully.',
            )
        return err(
            message = 'Validation failed.',
            details = serializer.errors,
        )

    # ── DELETE ────────────────────────────────────────────────────────────
    name = employee.full_name
    employee.delete()   # CASCADE deletes all related attendance records
    return ok(
        data    = None,
        message = f'Employee "{name}" and all associated records deleted successfully.',
    )


# ── Department choices ────────────────────────────────────────────────────────

@api_view(['GET'])
def department_list(request):
    """
    GET /api/departments/
    Returns all valid department choices as { value, label } pairs.
    Used by the frontend to populate <select> dropdowns.
    """
    departments = [
        {'value': d[0], 'label': d[1]}
        for d in Department.choices
    ]
    return ok({'departments': departments})


# ── Dashboard summary ─────────────────────────────────────────────────────────

@api_view(['GET'])
def dashboard_summary(request):
    """
    GET /api/dashboard/
    Returns high-level stats shown on the Dashboard page:
      - total_employees
      - today_present / today_absent / today_marked
      - department_breakdown (list of {department, count})
      - today (ISO date string, for display)
    """
    from attendance.models import Attendance   # local import avoids circular dependency

    today = datetime.date.today()

    total_employees = Employee.objects.count()

    today_present = Attendance.objects.filter(date=today, status='Present').count()
    today_absent  = Attendance.objects.filter(date=today, status='Absent').count()
    today_marked  = today_present + today_absent

    dept_breakdown = list(
        Employee.objects
        .values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return ok({
        'total_employees':    total_employees,
        'today_present':      today_present,
        'today_absent':       today_absent,
        'today_marked':       today_marked,
        'department_breakdown': dept_breakdown,
        'today':              str(today),
    })