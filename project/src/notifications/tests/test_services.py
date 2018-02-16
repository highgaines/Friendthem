from unittest.mock import Mock, patch
from model_mommy import mommy

from django.conf import settings
from django.test import TestCase

from src.notifications.services import notify_user
from src.notifications.models import Notification

class NotifyUserTestCase(TestCase):
    def setUp(self):
        self.sender = mommy.make(settings.AUTH_USER_MODEL)
        self.recipient = mommy.make(settings.AUTH_USER_MODEL, notifications=True)
        self.device = mommy.make('Device', user=self.recipient)
        self.msg = 'Test Message'

    @patch('src.notifications.services.onesignal')
    def test_send_notification(self, onesignal):
        client = Mock()
        response = Mock()
        response.ok = True
        client.send_notification.return_value = response
        notification = Mock()
        onesignal.Client.return_value = client
        onesignal.Notification.return_value = notification

        notify = notify_user(self.sender, self.recipient, self.msg)

        onesignal.Client.assert_called_once_with(app={
            'app_auth_key': settings.ONESIGNAL_APP_KEY,
            'app_id': settings.ONESIGNAL_APP_ID
        })

        onesignal.Notification.assert_called_once_with(contents={'en': self.msg})
        notification.set_parameter.assert_called_once_with(
            'headings', {'en': 'FriendThem'}
        )
        notification.set_target_devices.assert_called_once_with([self.device.device_id])
        client.send_notification.assert_called_once_with(notification)

        assert Notification.objects.first().message == self.msg

        assert notify == True

    @patch('src.notifications.services.onesignal')
    def test_do_not_send_notification_if_user_deactivated_notifications(self, onesignal):
        self.recipient.notifications = False
        self.recipient.save()

        notify = notify_user(self.sender, self.recipient, self.msg)

        onesignal.Client.assert_not_called()
        onesignal.Notification.assert_not_called()

        assert notify == False

    @patch('src.notifications.services.onesignal')
    def test_do_not_send_notification_if_user_dont_have_devices(self, onesignal):
        self.device.delete()

        notify = notify_user(self.sender, self.recipient, self.msg)

        onesignal.Client.assert_not_called()
        onesignal.Notification.assert_not_called()

        assert notify == False

    @patch('src.notifications.services.onesignal')
    def test_do_not_send_notification_if_already_sent(self, onesignal):
        mommy.make(Notification, message=self.msg, sender=self.sender, recipient=self.recipient)

        notify = notify_user(self.sender, self.recipient, self.msg)

        onesignal.Client.assert_not_called()
        onesignal.Notification.assert_not_called()

        assert notify == True
