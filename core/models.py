from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
import secrets

# Create your models here.
def numeric_validator(value):
    if not value.isnumeric():
        raise ValidationError(_("This field should only contain numbers"))
def phone_validator(value):
    if not value.isnumeric():
        raise ValidationError(_("The phone number is not a number"))
    if len(value) != 11:
        raise ValidationError(_("The phone number should be 11 digits"))
    phone_start_number = ['081','080','090','091','070']
    if value[:3]  in phone_start_number:
        pass
    else:
        raise ValidationError(_("Enter a valid nigerian number"))

def alpha_validator(value):
    if not value.isalpha():
        raise ValidationError(_("This field should only contain alphabets"))

class BaseManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
class User(AbstractUser):
    username = None
    email = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    objects = BaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField("First Name",max_length=55,validators=[alpha_validator])
    lastname = models.CharField("Last Name",max_length=55,validators=[alpha_validator])
    dob = models.DateField("Date of Birth", blank=True, null=True)
    gender = models.CharField(max_length=10,choices=(('M','Male'),('F','Female')))
    phonenumber = models.CharField(_('Phone Number'),max_length=11,validators = [phone_validator],
        help_text=_('Required. 11 Nigeria Phone Numbers.'),error_messages={
            'max_length': _("11 Numbers required."),
        },unique=True, blank=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    lga = models.CharField("Local Government Area",max_length=50, blank=True, null=True)
    hometown = models.CharField("Home Town",max_length=50, blank=True, null=True)
    residential_address = models.TextField(default="Prefer not to say",blank=True,max_length=1000)
    driver_license_no = models.CharField(max_length=12)
    occupation = models.CharField(max_length=70)

    def __str__(self):
        return self.user.email

class VehicleMake(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return "{} - {}".format(self.make.name,self.name)

class QuoteInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_year = models.BigIntegerField()
    vehicle_make = models.ForeignKey(VehicleMake, on_delete=models.SET_NULL, null=True,blank=True)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.SET_NULL, null=True,blank=True)
    coverage = models.CharField(max_length=20, choices= (("basic", "Basic"),("comprehensive","Comprehensive")))
    vehicle_identification_number = models.CharField(max_length=20)
    expired = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_approved_payment = models.DateTimeField(blank=True, null=True)


    def __str__(self) :
        return self.user.email

class Quote(models.Model):
    information = models.OneToOneField(QuoteInformation,on_delete=models.CASCADE)
    price = models.BigIntegerField()

    def __str__(self):
        return self.information.user.email
    
class Payment(models.Model):
    quote = models.ForeignKey(QuoteInformation, on_delete=models.SET_NULL, null=True)
    amount = models.BigIntegerField()
    status = models.CharField(max_length=2, choices=(("a","Approved"),("p","Pending"),("f","Failed"),("c","Cancelled")), default="p")
    ref = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(blank=True, null=True)

    def save(self,*args,**kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            similar_ref =Payment.objects.filter(ref=ref)
            if not similar_ref.exists():
                self.ref = ref
                break
        super().save(*args,**kwargs)

    def __str__(self):
        return self.quote.user.email

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=12)
    message = models.CharField(max_length=400)
    read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

class Feedback(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200,blank=True,null=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


