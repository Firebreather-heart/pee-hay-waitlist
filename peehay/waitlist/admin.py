from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import WaitlistEntry


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = [
        'position',
        'email',
        'role_display',
        'status_badge',
        'priority_badge',
        'days_waiting_display',
        'created_at',
    ]

    list_filter = [
        'status',
        'priority',
        'role',
        'created_at',
    ]

    search_fields = [
        'email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'days_waiting_display',
        'position',
    ]

    fieldsets = (
        ('User Information', {
            'fields': (
                'email',
                'role',
            )
        }),
        ('Admin Settings', {
            'fields': (
                'status',
                'priority',
                'position',
                'admin_notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'days_waiting_display',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['position', 'created_at']

    list_per_page = 50

    actions = [
        'mark_as_approved',
        'mark_as_contacted',
        'mark_as_rejected',
        'set_high_priority',
        'set_low_priority',
    ]

    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'contacted': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        """Display priority with color coding"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'urgent': 'darkred',
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'

    def days_waiting_display(self, obj):
        """Display days waiting with formatting"""
        days = obj.days_waiting
        if days == 0:
            return "Today"
        elif days == 1:
            return "1 day"
        else:
            return f"{days} days"
    days_waiting_display.short_description = 'Days Waiting'

    def role_display(self, obj):
        """Display role with formatting"""
        if obj.role:
            return obj.get_role_display()
        return '-'
    role_display.short_description = 'Role/Use Case'

    # Admin actions
    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} entries marked as approved.')
    mark_as_approved.short_description = 'Mark selected entries as approved'

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f'{updated} entries marked as contacted.')
    mark_as_contacted.short_description = 'Mark selected entries as contacted'

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} entries marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected entries as rejected'

    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} entries set to high priority.')
    set_high_priority.short_description = 'Set selected entries to high priority'

    def set_low_priority(self, request, queryset):
        updated = queryset.update(priority='low')
        self.message_user(request, f'{updated} entries set to low priority.')
    set_low_priority.short_description = 'Set selected entries to low priority'


# Customize admin site headers
admin.site.site_header = "Waitlist Administration"
admin.site.site_title = "Waitlist Admin"
admin.site.index_title = "Welcome to Waitlist Administration"
