from django import forms
from django.contrib.auth import authenticate
from django.contrib import messages
from .models import User, Profile, QuoteInformation, Payment, Quote
from .payment import Paystack
from django.urls import reverse
import random
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget= forms.PasswordInput, strip =False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        self.user  = authenticate(self.request,email = email,password=password)
        if not self.user:
            raise forms.ValidationError("Incorrect Credentials")
        return self.cleaned_data
    def get_user(self):
        return self.user
    
class RegistrationForm(forms.ModelForm):
    # department = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}),required=False)
    email= forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput,required = False,min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, required = False)
    class Meta:
        model = Profile
        exclude = ['user']
    def clean(self):
        email = self.cleaned_data.get('email')
        if not email:
            self.add_error('email','Email is required')
        if not self.cleaned_data.get('password'):
            self.add_error('password','Password is required')
        if User.objects.filter(email = email).exists():
            self.add_error('email','User already Exists')
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            self.add_error('password2',"Passwords deos not match")
        return self.cleaned_data
    
class QuoteForm(forms.ModelForm):
    class Meta:
        model = QuoteInformation
        fields = "__all__"
    def generate_quote(self,request,main_data):
        moneys = [80000,90000,110000,40000,120000,200000,150000,170000,70000]
        amount = random.choice(moneys)
        data = self.cleaned_data
        quote_info = main_data
        Quote.objects.create(information = quote_info,price = amount)
        payment = Payment()
        payment.quote = quote_info
        payment.amount = amount        
        payment.save()
        payment_gateway = Paystack()
        response = payment_gateway.initalize_payment(
            request.user.email,payment.amount,
            ref = payment.ref, 
            success_url= request.build_absolute_uri(
            reverse("verify-payment", kwargs={'ref':payment.ref}))
            )
        if response['status']:
            success_url = response["data"]["authorization_url"]
        else:
            success_url = reverse("quote-details",kwargs={'pk':main_data.id})
            messages.error(request,response['message'])
            payment.status = "c"
            payment.save()
        return success_url