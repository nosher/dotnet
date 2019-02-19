from django.db import models
import datetime
import django


class ArchiveItems(models.Model):

    adid = models.CharField(max_length=60)
    company = models.CharField(max_length=60)
    year = models.CharField(max_length=30)
    type = models.CharField(max_length=60)
    source = models.CharField(max_length=90)
    model = models.CharField(max_length=45)
    date_created = models.DateTimeField(django.utils.timezone.now)

    class Meta:
        ordering = ('-year', "company")

    def __unicode__(self):
        return self.year + ": " + self.company

    def getCount(self):
        return self.__count

    def setCount(self, count):
        self.__count = count

    def getHasNew(self):
        return self.__hasNew

    def setHasNew(self, hasNew):
        self.__hasNew = hasNew

    def getPrimary(self):
        return self.adid.split(",")[0]

    def getTitle(self):
        return self.company.replace("/", " / ")

    def isRecentArchive(self):
        return ((datetime.datetime.now() - self.date_created) < datetime.timedelta(days = 35))

    count = property(getCount, setCount)
    hasNew = property(getHasNew, setHasNew)
    isNew = property(isRecentArchive)

