from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Notification


@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):

    # When order first created
    if created:
        Notification.objects.create(
            user=instance.user,
            title="Order Placed",
            message=f"Order #{instance.id} placed successfully."
        )

    # When order updated
    else:
        Notification.objects.create(
            user=instance.user,
            title="Order Update",
            message=f"Order #{instance.id} status updated to {instance.status}"
        )
