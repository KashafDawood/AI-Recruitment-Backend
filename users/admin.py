from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Candidate, Employer

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'role', 'photo', 'phone', 'website', 'socials')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Candidate)
admin.site.register(Employer)
