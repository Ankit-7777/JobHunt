from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Recruiter, Employee, Job, Application


class UserAdmin(BaseUserAdmin):
    list_display = ( 'id','email','name', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'role', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('role','name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser')}
        ),
    )


class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'website', 'created_at', 'updated_at')
    search_fields = ('user__email', 'company_name')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location')
    search_fields = ('user__email', 'phone_number', 'location')
    ordering = ('user',)


class JobAdmin(admin.ModelAdmin):
    list_display = ( 'id','title', 'recruiter', 'location', 'job_type', 'salary', 'posted_date', 'application_deadline')
    search_fields = ('title', 'recruiter__user__email', 'location', 'job_type')
    list_filter = ('job_type', 'posted_date', 'application_deadline')
    ordering = ('-posted_date',)



class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'job', 'submitted_at', 'status')
    search_fields = ('employee__user__email', 'job__title', 'status')
    list_filter = ('status', 'submitted_at')
    ordering = ('-submitted_at',)



admin.site.register(User, UserAdmin)
admin.site.register(Recruiter, RecruiterAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
