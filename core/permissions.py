from rest_framework.permissions import BasePermission
from jobs.models import JobListing


class RoleBasedPermission(BasePermission):
    """
    Base class for role-based permissions
    """

    allowed_roles = []
    message = "User does not have the required role."

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role in self.allowed_roles


class IsCandidate(RoleBasedPermission):
    allowed_roles = ["candidate"]
    message = "Only candidates are allowed to perform this action."


class IsEmployer(RoleBasedPermission):
    allowed_roles = ["employer"]
    message = "Only employers are allowed to perform this action."


class IsCandidateOrEmployer(RoleBasedPermission):
    allowed_roles = ["candidate", "employer"]
    message = "Only candidates or employers are allowed to perform this action."


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    """

    message = "You must be the owner of this object."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # Ensure obj has either user or created_by field
        user_field = getattr(obj, "user", None) or getattr(obj, "created_by", None)
        return user_field == request.user


class IsOwnerOrEmployerReadOnly(BasePermission):
    """
    Object-level permission to only allow owners to edit,
    but employers can read.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # Read permissions are allowed to employers
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user.role == "employer" or obj.user == request.user

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsEmployerAndOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.employer == request.user


class IsJobEmployer(BasePermission):
    """
    Custom permission to only allow employers of a job to access the job's applications.
    """

    message = "You must be the employer of this job to view its applications."

    def has_permission(self, request, view):
        job_id = view.kwargs.get("job_id")
        if job_id:
            try:
                job = JobListing.objects.get(id=job_id)
                return job.employer == request.user
            except JobListing.DoesNotExist:
                return False
        return False
