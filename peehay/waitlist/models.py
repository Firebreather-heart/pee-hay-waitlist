from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class WaitlistEntry(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('contacted', 'Contacted'),
    ]

    ROLE_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('manager', 'Manager'),
        ('student', 'Student'),
        ('business_owner', 'Business Owner'),
    ]

    # Core user information
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="User's email address"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        help_text="User's role or use case (optional)"
    )

    # Admin fields
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level set by admin"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for admin use"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the entry was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the entry was last updated"
    )
    position = models.PositiveIntegerField(
        editable=False,
        help_text="Position in waitlist (auto-calculated)"
    )

    class Meta:
        ordering = ['position', 'created_at']
        verbose_name = "Waitlist Entry"
        verbose_name_plural = "Waitlist Entries"

    def __str__(self):
        return f"{self.email} - {self.get_status_display()}"  # type:ignore

    def save(self, *args, **kwargs):
        # Auto-assign position if this is a new entry
        if not self.pk and not self.position:
            last_position = WaitlistEntry.objects.aggregate(
                models.Max('position')
            )['position__max']
            self.position = (last_position or 0) + 1
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Return email as display name"""
        return self.email

    @property
    def days_waiting(self):
        """Calculate how many days the user has been waiting"""
        return (timezone.now() - self.created_at).days
