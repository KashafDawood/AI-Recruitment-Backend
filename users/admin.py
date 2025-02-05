from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, EmployerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'photo', 'phone', 'website', 'socials')}),
    )

    def get_roles(self, obj):
        roles = []
        if hasattr(obj, 'candidate_profile'):
            roles.append('Candidate')
        if hasattr(obj, 'employer_profile'):
            roles.append('Employer')
        return ', '.join(roles) if roles else 'No Role'
    
    get_roles.short_description = 'Roles'
    list_display = ('username', 'email', 'name', 'get_roles', 'is_staff')

admin.site.register(User, CustomUserAdmin)
admin.site.register(CandidateProfile)
admin.site.register(EmployerProfile)
