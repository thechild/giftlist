from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist

def get_person_from_user(user):
    try:
        # do we already have the user? If so, just return it
        p = Person.objects.get(login_user=user)
    except ObjectDoesNotExist as dne:
        try:
            # now, let's check to see if someone has already added this email address
            p = Person.objects.get(email = user.email)
            p.login_user = user
            p.save()
        except ObjectDoesNotExist as dne:
            # nope, let's create a brand new person
            p = Person()
            p.login_user = user
            p.first_name = user.first_name
            p.last_name = user.last_name
            p.email = user.email
            p.save()
    
    return p

def clear_reserved_gifts(myself, recipient):
    for g in Gift.objects.filter(recipient=recipient).filter(reserved_by=myself):
        g.reserved_by = None
        g.date_reserved = None
        if g.secret:
            g.delete()
        else:
            g.save()

def get_reserved_gift(myself, recipient):
    selected_gift = Gift.objects.filter(recipient=recipient).filter(reserved_by=myself)
    if selected_gift.count() == 1:
        return selected_gift[0]
    elif selected_gift.count() > 1:
        print "There were multiple gifts from %s to %s.  Returned the first one." % (myself, recipient)
        return selected_gift[0]
    else:
        return None

class Person(models.Model):
    login_user = models.ForeignKey(User, related_name='django user', blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def gifts(self):
        return Gift.objects.filter(recipient=self).exclude(secret=True)

    def name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return self.name()

class Gift(models.Model):
    recipient = models.ForeignKey(Person)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    price = models.CharField(max_length=100, blank=True)
    secret = models.BooleanField(default=False)
    date_added = models.DateTimeField('date created', auto_now_add=True, blank=True)
    reserved_by = models.ForeignKey(Person, related_name='Gift Reservor', blank=True, null=True)
    date_reserved = models.DateTimeField('date reserved', blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.title, self.recipient)

class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'email')

class GiftForm(ModelForm):
    class Meta:
        model = Gift
        fields = ('title', 'description', 'url', 'price')