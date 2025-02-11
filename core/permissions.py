from rest_framework.permissions import BasePermission


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
        # Check if the user is authenticated and is the employer who created the job listing
        return request.user.is_authenticated and obj.employer == request.user
