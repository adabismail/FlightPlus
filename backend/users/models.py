from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
 
 
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)  # lowercases the domain part
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)          # hashes the password
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email         = models.EmailField(unique=True)       # login identifier
    name          = models.CharField(max_length=150)
    phone         = models.CharField(max_length=20, blank=True, null=True)
    notify_email  = models.BooleanField(default=True)    # send email alerts?
    notify_sms    = models.BooleanField(default=False)   # send SMS alerts?
    currency      = models.CharField(max_length=3, default='INR')
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    date_joined   = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
 
    objects = UserManager()    # plug in our custom manager
 
    USERNAME_FIELD  = 'email'  # use email to log in
    REQUIRED_FIELDS = ['name'] # required when creating superuser
 
    class Meta:
        db_table = 'users'     # exact table name in PostgreSQL
