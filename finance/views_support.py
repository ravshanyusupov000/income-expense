from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .models import SupportTicket
import re
from django.http import JsonResponse
from django.utils.translation import gettext as _


@require_POST
@login_required
def support_quick(request):
    try:
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not subject or not message:
            return JsonResponse(
                {"ok": False, "error": _("Fill all fields")},
                status=400
            )

        SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message
        )

        return JsonResponse({
            "ok": True,
            "message": _("Your message has been sent successfully")
        })


    except Exception as e:
        print("SUPPORT ERROR:", e)
        return JsonResponse(
            {"ok": False, "error": str(e)},
            status=500
        )

@require_POST
@login_required
def support_quick_create(request):
    try:
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not re.fullmatch(r"\+998\d{9}", phone):
            return JsonResponse(
                {"ok": False, "error": _("Enter phone number in +998XXXXXXXXX format")},
                status=400
            )

        if not subject or not message:
            return JsonResponse(
                {"ok": False, "error": _("Fill all fields")},
            status=400)

        SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            phone_number = phone
        )

        return JsonResponse({
            "ok": True,
            "message": _("Your message has been sent successfully")
        })


    except Exception as e:
        print("SUPPORT ERROR:", e)
        return JsonResponse(
            {"ok": False, "error": str(e)},
            status=500
        )
