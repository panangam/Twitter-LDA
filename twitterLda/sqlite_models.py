# -*- coding: utf-8 -*-

# sqlite_models.py

from twitterLda.projectPath import datadir

import codecs
import peewee as pw
import ujson
import os

dbdir = os.path.join(datadir, 'db')
db = pw.SqliteDatabase(os.path.join(dbdir, '10-27.sqlite'))

class BaseModel(pw.Model):
    """
    Parent database model for all database Models. Insures proper parameters in created Models.
    """
    class Meta:
        """Sets model parameters."""
        database = db


class User(BaseModel):
    """
    ORM model of the User table
    """
    id = pw.CharField(unique=True, primary_key=True)
    lastname = pw.CharField(null=True)
    firstname = pw.CharField(null=True)
    shout_count = pw.IntegerField()


class Venue(BaseModel):
    """
    ORM model of the Venue table
    """
    id = pw.CharField(unique=True, primary_key=True)
    name = pw.CharField()
    city = pw.CharField(null=True)
    state = pw.CharField(null=True)
    zip = pw.CharField(null=True)
    cat_id = pw.CharField(null=True)
    cat_name = pw.CharField(index=True, null=True)
    shout_count = pw.IntegerField()


class UserVenue(BaseModel):
    """
    Intermediate table for the many-to-many relationship between User and Venue.
    """
    user = pw.ForeignKeyField(User, on_delete='CASCADE', on_update='CASCADE')
    venue = pw.ForeignKeyField(Venue, on_delete='CASCADE', on_update='CASCADE')


class Checkin(BaseModel):
    """
    ORM model of the Checkin table
    """
    id = pw.CharField(unique=True, primary_key=True)
    shout = pw.TextField()
    date = pw.DateField()
    time = pw.TimeField()
    weekday = pw.IntegerField()
    user = pw.ForeignKeyField(User, related_name='checkins', on_delete='SET NULL', on_update='CASCADE')
    venue = pw.ForeignKeyField(Venue, related_name='checkins', on_delete='CASCADE', on_update='CASCADE')

def test():
    db.connect()
    User.create(
        id=1,
        lastname='testlast',
        firstname='testfirst',
        shout_count=0
        )
    db.close()

def main():
    pass

if __name__ == '__main__':
    main()
