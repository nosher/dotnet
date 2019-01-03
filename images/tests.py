import datetime

from django.utils import timezone
from django.test import TestCase
from .models import PhotoAlbum


class PhotoAlbumModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() - datetime.timedelta(days=60)
        old_album = PhotoAlbum(date_created=time)
        self.assertIs(old_album.isRecentAlbum(), True)
