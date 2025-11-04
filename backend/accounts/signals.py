from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.dispatch import receiver
from .models import Contact


# Once the email is set up in settings.py, uncomment the following code and remove the above code


@receiver(post_save, sender=Contact)
def send_contact_email(sender, instance, created, **kwargs):
    if created:
        subject = "Thank You for Contacting Us!"
        context = {"name": instance.name, "message": instance.message}
        html_message = render_to_string("emails/contact_email.html", context)
        plain_message = strip_tags(html_message)
        from_email = "noreply@example.com"  # Use your Gmail
        recipient_list = [instance.email]

        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
        )
