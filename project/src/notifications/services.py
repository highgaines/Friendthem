import onesignal
from django.conf import settings
from src.notifications.models import Notification

def notify_user(sender, recipient, msg):
    device_ids = recipient.device_set.all().values_list('device_id', flat=True)
    notification, created = Notification.objects.get_or_create(
        message=msg,
        sender=sender,
        recipient=recipient
    )

    if recipient.notifications and device_ids and created:
        client = onesignal.Client(
            app={
            'app_auth_key': settings.ONESIGNAL_APP_KEY,
            'app_id': settings.ONESIGNAL_APP_ID
        })

        notification = onesignal.Notification(content={'en': msg})
        notification.set_parameter('headings', {'en': 'FriendThem'})

        notification.set_target_devices(list(device_ids))

        response = client.send_notification(notification)
        return response.ok
    return recipient.notifications and bool(device_ids)
