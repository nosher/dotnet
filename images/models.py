from django.db import models
import datetime
import django

from ..constants import * 

class AlbumYears(models.Model):

    year = models.CharField(max_length=30)
    description = models.TextField()
    xorder = models.IntegerField()

    class Meta:
        ordering = ('xorder', '-year')

    def __str__(self):
        return self.year + ": " + self.description

    def getCount(self):
        return self.__count

    def setCount(self, count):
        self.__count = count

    def getHasNew(self):
        return self.__hasNew

    def setHasNew(self, hasNew):
        self.__hasNew = hasNew

    count = property(getCount, setCount)
    hasNew = property(getHasNew, setHasNew)


class AlbumGroup(models.Model):

    title = models.CharField(max_length=200)
    latlong = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title


class PhotoAlbums( models.Model ):

    year = models.CharField( max_length=30 )
    description = models.TextField()
    xorder = models.IntegerField()

    class Meta:
        ordering = ('xorder', '-year')

    def __str__(self):
        return self.year + ": " + self.description

    def getCount( self ):
        return self.__count

    def setCount( self, count ):
        self.__count = count

    def getHasNew( self ):
        return self.__hasNew

    def setHasNew( self, hasNew ):
        self.__hasNew = hasNew

    count = property( getCount, setCount)
    hasNew = property( getHasNew, setHasNew)

class PhotoAlbum(models.Model):

    year = models.CharField(max_length = 30)
    path = models.CharField(max_length = 255)
    title = models.CharField(max_length = 255)
    description = models.TextField(db_index = True)
    date_created = models.DateTimeField(default = django.utils.timezone.now)
    group = models.ForeignKey(AlbumGroup, default = 0, on_delete=models.PROTECT)

    def __str__(self):
        return self.year + ": " + self.title

    def getIsRecent(self):
        try:
            year = self.date_created.year
            month = self.date_created.month
            day = self.date_created.day
            diff = datetime.datetime.now() - datetime.datetime(year, month, day)
        except: 
            diff = datetime.timedelta(70)
        return diff.days < NEW_PHOTO_CUTOFF 

    def setIsRecent(self):
        pass

    def getIsFirstInGroup(self):
        return self.__isfirst

    def setIsFirstInGroup(self, isfirst):
        self.__isfirst = isfirst

    def getIsLastInGroup(self):
        return self.__islast

    def setIsLastInGroup(self, islast):
        self.__islast = islast

    def getIsJoinedInGroup(self):
        return self.__isjoined

    def setIsJoinedInGroup(self, isjoined):
        self.__isjoined = isjoined

    isFirst = property(getIsFirstInGroup, setIsFirstInGroup)
    isLast= property(getIsLastInGroup, setIsLastInGroup)
    isJoined= property(getIsJoinedInGroup, setIsJoinedInGroup)
    is_new = property(getIsRecent, setIsRecent)
