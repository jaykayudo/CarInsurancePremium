from django.urls import path
from django.views.generic import TemplateView
from . import views



urlpatterns = [
    path("",TemplateView.as_view(template_name="index.html"), name="index"),
    path("login/",views.LoginView.as_view(),name="login"),
    path("signup/",views.SignUpView.as_view(),name="signup"),
    path("dashboard/",TemplateView.as_view(template_name = "dashboard/dashboard.html"),name="dashboard"),
    path("quote/",views.QuoteListView.as_view(),name="quote-list"),
    path("quote/add/",views.QuoteCreateView.as_view(),name="quote-create"),
    path("quote/<int:pk>/",views.QuoteDetailView.as_view(),name="quote-details"),
    path("quote/<int:id>/make-payment/",views.MakePayment.as_view(),name="make-payment"),
    path("quote/<slug:ref>/verify-payment/",views.VerifyPayment.as_view(),name="verify-payment"),
    path("feedback/",views.FeedbackCreateView.as_view(),name="feedback"),
    path("notification/",views.NotificationList.as_view(),name="notification"),
    path("user-profile/",views.ProfileUpdateView.as_view(),name="user-profile"),
    path("payment-successful/",views.payment_successful,name="payment-successful"),
    path("get-vehicle-model/",views.get_vehicle_models,name="get-vehicle-models"),
    path("logout/",views.logoutview,name="logout"),
]
