from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from random import randint
from django.utils import timezone

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

# Create your models here.
class MyUser(AbstractBaseUser , PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=True, help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(auto_now_add = True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    phone = models.CharField(max_length = 10, null = True)
    confirmed_email = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = "users"


def create_otp(user = None, purpose = None):
    if not user:
        raise ValueError("Invalid Arguments");
    choices = []
    for choice_purpose, verbose in UserOTP.OTP_PURPOSE_CHOICES:
        choices.append(choice_purpose)
    if not purpose in choices:
        raise ValueError('Invalid Arguments');
    if UserOTP.objects.filter(user = user, purpose = purpose).exists():
        old_otp = UserOTP.objects.get(user = user, purpose = purpose)
        old_otp.delete();
    otp = randint(1000, 9999)
    otp_object = UserOTP.objects.create(user = user, purpose = purpose, otp = otp)
    return otp

def get_valid_otp_object(user = None, otp= None, purpose = None):
    if not user:
        raise ValueError("Invalid Arguments");
    choices = []
    for choice_purpose, verbose in UserOTP.OTP_PURPOSE_CHOICES:
        choices.append(choice_purpose)
    if not purpose in choices:
        raise ValueError('Invalid Arguments');
    try:
        otp_object = UserOTP.objects.get(user = user, purpose=purpose, otp=otp)
        return otp_object
    except UserOTP.DoesNotExist:
        return None

class UserOTP(models.Model):
    OTP_PURPOSE_CHOICES = (
        ('FP', 'Forgot Password'),
        ('AA', 'Activate Account'),
        ('CE', 'Confirm Email'),
    );
    user = models.ForeignKey(MyUser)
    otp = models.CharField(max_length = 4)
    purpose = models.CharField(max_length = 2, choices = OTP_PURPOSE_CHOICES)
    created_on = models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together= ['user', 'purpose']


class Trading_Platform(models.Model):
        PLATFORM_CHOICES = (
            ('Quadrigacx','Quadrigacx'),
            ('Kraken','Kraken'),
            ('Bitfinex','Bitfinex'),
            ('Quoine','Quoine'),
            ('Poloniex','Poloniex'),
            ('Bitmex','Bitmex')
            )
        user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
        trading_platform = models.CharField(max_length=100,
        choices=PLATFORM_CHOICES, default=None)
        api_key = models.CharField(max_length=224)
        secret = models.CharField(max_length=224)
        client_id = models.IntegerField(blank=True)

        def __unicode__(self):
        	    return self.user.email + " - " + self.trading_platform
