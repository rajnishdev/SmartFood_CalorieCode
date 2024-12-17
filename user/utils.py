from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

def send_verification_email(user, request):
    # Generate token and UID
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    )

    # Send email
    subject = "Verify Your Email Address"
    message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThank you!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
