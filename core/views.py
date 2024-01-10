from typing import Any, Dict, Optional
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, CreateView,DetailView,View, UpdateView
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from .forms import *
from .models import *
from .payment import Paystack

# Create your views here.

class LoginView(FormView):
    form_class = LoginForm
    template_name = "login.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request,user)
        messages.success(self.request,"Login Successful")
        return super().form_valid(form)
    
class SignUpView(FormView):
    form_class = RegistrationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')
    def form_valid(self,form):  
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = User.objects.create_user(email = email, password = password)
        user.save()
        obj = form.save(commit = False)
        obj.user = user
        obj.save()
        messages.success(self.request,"Sign Up Successful")
        message = "Thank you for signing up to our service. We offer a lovely lot. Make sure to create a quote and insure your vehicle."
        Notification.objects.create(user = self.request.user, subject = f"Welcome to CIP",
                                            message=message)
        return super().form_valid(form)

class QuoteListView(LoginRequiredMixin,ListView):
    template_name = "dashboard/quote.html"

    def get_queryset(self):
        return QuoteInformation.objects.filter(user = self.request.user)

class QuoteDetailView(LoginRequiredMixin,DetailView):
    model = QuoteInformation
    template_name = "dashboard/quote-details.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object  = self.get_object()
        payment = Payment.objects.filter(quote = object)
        context['payments'] = payment
        return context
    def get(self, request,*args, **kwargs):
        if self.get_object().user != request.user:
            return HttpResponseForbidden("Not Allowed")
        return super().get(request, *args, **kwargs)

class QuoteCreateView(LoginRequiredMixin,FormView):
    form_class = QuoteForm
    template_name = "dashboard/quote-form.html"
    success_url = reverse_lazy("quote-list")

    def form_valid(self, form):
        obj = form.save()
        url = form.generate_quote(self.request,obj)
        self.success_url = url
        return super().form_valid(form)



class MakePayment(LoginRequiredMixin,View):
    # def get(self,request,id):
    #     quote_info = get_object_or_404(QuoteInformation,id = id)
    #     context = {
    #         'quote_info': quote_info
    #     }
    #     return render(request,"dashboard/make-payment",context)
    def post(self,request,id):
        quote_info = get_object_or_404(QuoteInformation,id = id)
        payment = Payment()
        payment.quote = quote_info
        payment.amount = quote_info.quote.price
        
        payment.save()
        payment_gateway = Paystack()
        response = payment_gateway.initalize_payment(
            self.request.user.email,payment.amount,
            ref = payment.ref, 
            success_url= self.request.build_absolute_uri(
            reverse("verify-payment", kwargs={'ref':payment.ref}))
            )
        if response['status']:
            success_url = response["data"]["authorization_url"]
            return redirect(success_url)
        else:
            messages.error(self.request,response['message'])
            payment.status = "c"
            message = f"""
Your Payment of NGN {payment.amount} for {quote_info.vehicle_make.name} {quote_info.vehicle_model.name} failed. 
Please try again later or try a different payment method. Thank you for using our service.
"""
                
            Notification.objects.create(user = request.user, subject = f"Quote payment for {quote_info.vehicle_make.name}",
                                            message=message)
            payment.save()
        return  redirect(reverse("quote-details",kwargs={'pk':id}))

class VerifyPayment(LoginRequiredMixin,View):
    def get(self,request,ref):
        payment_gateway = Paystack()
        response = payment_gateway.verify_payment(ref)
        if response['status']:
            try:
                payment = Payment.objects.get(ref = ref)
                payment.status = 'a'
                payment.date_approved = timezone.now()
                payment.save()

                quote_info = QuoteInformation.objects.get(id = payment.quote.id)
                quote_info.last_approved_payment = timezone.now()
                quote_info.expired = False
                quote_info.save()
                message = f"""
Your Payment of NGN {payment.amount} for {quote_info.vehicle_make.name} {quote_info.vehicle_model.name}  was successful. 
Thank you for continuing with our service.
"""
                
                Notification.objects.create(user = request.user, subject = f"Quote payment for {quote_info.vehicle_make.name}",
                                            message=message)
            except Payment.DoesNotExist:
                messages.error(request,_("unknown transaction"))
                return redirect("quote-list")
        else:
            messages.error(request,_(response['message']))
            return redirect(reverse("quote-list"))
        
        return redirect(reverse("payment-successful"))

class FeedbackCreateView(LoginRequiredMixin,CreateView):
    model = Feedback
    template_name = "dashboard/feedback.html"
    fields = "__all__"
    success_url = reverse_lazy("feeedback-form")

    def form_valid(self, form):
        messages.success(self.request,"Feedback Sent. We will get to you shortly via email.")
        return super().form_valid(form)

class NotificationList(LoginRequiredMixin,ListView):
    template_name = "dashboard/notification-list.html"

    def get_queryset(self):
        notification = Notification.objects.filter(user = self.request.user)
        return notification

def payment_successful(request):
    return render(request,"dashboard/payment-successful.html")

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = Profile
    fields = "__all__"
    template_name = "dashboard/user-profile.html"
    success_url = reverse_lazy("profile") 

    def get_object(self):
        return Profile.objects.get(user = self.request.user)
    
def get_vehicle_models(request):
    id = request.GET['id']
    vehicle_make = VehicleMake.objects.get(id = id)
    model = VehicleModel.objects.filter(make = vehicle_make)
    model = model.values_list("name","id")
    # print(model)
    return JsonResponse({'models':list(model)},safe=True)


def logoutview(request):
    logout(request)
    messages.success(request,"Logout Successful")
    return redirect("login")
