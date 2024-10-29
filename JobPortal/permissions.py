from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsRecruiterOrSuperadmin(BasePermission):
    """
    Custom permission to allow only recruiters and superadmins to create jobs.
    Employees can view all jobs but cannot create or edit any jobs.
    Recruiters can perform all actions on jobs they created.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (
            request.user.role == 'recruiter' or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == 'recruiter':
            return obj.recruiter.user == request.user
        return request.user.is_superuser

class IsEmployeeRecruiterOrSuperadmin(BasePermission):
    """
    Custom permission to allow:
    - Employees to create, view, update, and delete their own applications.
    - Recruiters to view applications for jobs they've posted.
    - Superadmins to view and delete applications only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            if request.method in ('GET', 'DELETE'):
                return True
            return False

        if request.user.role == 'employee':
            if request.method in ('GET', 'PUT', 'PATCH', 'DELETE'):
                return obj.employee.user == request.user
        
        elif request.user.role == 'recruiter':
            if request.method == 'GET':
                return obj.job.recruiter.user == request.user
        return False

