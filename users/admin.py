from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import redirect

from club.exceptions import AccessDenied
from common.data.achievements import ACHIEVEMENTS
from common.data.hats import HATS
from users.models import UserBadge


def do_user_admin_actions(request, user, data):
    if not request.me.is_moderator:
        raise AccessDenied()

    if user.is_god and not settings.DEBUG:
        raise AccessDenied(title="На этого юзера нельзя псить")

    # Hats
    if data["remove_hat"]:
        user.hat = None
        user.save()

    if data["add_hat"]:
        if data["new_hat"]:
            hat = HATS.get(data["new_hat"])
            if hat:
                user.hat = {"code": data["new_hat"], **hat}
                user.save()
        else:
            user.hat = {
                "code": "custom",
                "title": data["new_hat_name"],
                "icon": data["new_hat_icon"],
                "color": data["new_hat_color"],
            }
            user.save()

    # Achievements
    if data["add_achievement"]:
        achievement = ACHIEVEMENTS.get(data["new_achievement"])
        if achievement:
            UserBadge.objects.get_or_create(
                user=user,
                type=data["new_achievement"],
                defaults=dict(
                    name=achievement["title"],
                    image=achievement["icon"],
                    description=achievement.get("description"),
                    style=achievement.get("style"),
                ),
            )

    # Ban
    if data["is_banned"]:
        user.is_banned_until = datetime.utcnow() + timedelta(
            days=data["ban_days"] or 9999999
        )
        user.save()
        # TODO: send email/bot with data["ban_reason"]

    # Unmoderate
    if data["is_rejected"]:
        user.is_profile_rejected = True
        user.save()

    return redirect("profile", user.slug)
