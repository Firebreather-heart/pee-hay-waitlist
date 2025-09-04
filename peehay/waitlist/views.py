from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from ninja import NinjaAPI, Schema
from typing import Optional
from django.http import HttpResponseBadRequest

from .models import WaitlistEntry


# Pydantic schemas for Django Ninja
class WaitlistEntryCreateSchema(Schema):
    email: str
    role: Optional[str] = None


class WaitlistEntryResponseSchema(Schema):
    id: int
    email: str
    role: Optional[str]
    position: int
    created_at: datetime
    status: str


class StatsSchema(Schema):
    total_signups: int
    this_week: int
    this_month: int


# Initialize the API
api = NinjaAPI(title="Waitlist API", version="1.0.0",
               description="Public API for joining the waitlist")


@api.post("/waitlist/join/", response=WaitlistEntryResponseSchema)
def join_waitlist(request, data: WaitlistEntryCreateSchema):
    """Join the waitlist"""
    # Check if email already exists
    if WaitlistEntry.objects.filter(email=data.email.lower()).exists():
        return HttpResponseBadRequest("Email already exists in waitlist")

    # Create entry
    entry = WaitlistEntry.objects.create(
        email=data.email.lower(),
        role=data.role
    )

    return {
        "id": entry.pk,
        "email": entry.email,
        "role": entry.role,
        "position": entry.position,
        "created_at": entry.created_at,
        "status": entry.status
    }


@api.get("/waitlist/status/{email}/", response=WaitlistEntryResponseSchema)
def get_waitlist_status(request, email: str):
    """Get waitlist status by email"""
    try:
        entry = WaitlistEntry.objects.get(email=email.lower())
        return {
            "id": entry.pk,
            "email": entry.email,
            "role": entry.role,
            "position": entry.position,
            "created_at": entry.created_at,
            "status": entry.status
        }
    except WaitlistEntry.DoesNotExist:
        return api.create_response(
            request,
            {"detail": "Email not found in waitlist"},
            status=404
        )


@api.get("/waitlist/stats/", response=StatsSchema)
def public_stats(request):
    """Get public waitlist statistics"""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_signups = WaitlistEntry.objects.count()
    this_week = WaitlistEntry.objects.filter(created_at__gte=week_ago).count()
    this_month = WaitlistEntry.objects.filter(
        created_at__gte=month_ago).count()

    return {
        "total_signups": total_signups,
        "this_week": this_week,
        "this_month": this_month
    }
