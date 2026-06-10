from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import uuid


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        email = data.get("email", "")

        if not user.username:
            base = slugify(email.split("@")[0])
            user.username = f"{base}_{uuid.uuid4().hex[:6]}"

        return user