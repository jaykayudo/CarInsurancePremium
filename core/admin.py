from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *



class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None,{"fields":("email","password")}),
        ("Personal info",{"fields":("first_name","last_name")}),
        ("Permission",{"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates",{"fields":("last_login","date_joined")}),
    )
    add_fieldsets = ((None,{"classes":("wide",),"fields":("email","password1","password2")}))

    list_display = ("email","first_name","last_name","is_staff")
    search_fields = ("email","first_name","last_name")
    ordering = ("email",)

# Register your models here.
class CIPAdminSite(admin.sites.AdminSite):
    site_title = "CIP Admin"
    site_header = "CIP Admin"


cip_admin = CIPAdminSite()
cip_admin.register(User, UserAdmin)
cip_admin.register(Quote)
cip_admin.register(QuoteInformation)
cip_admin.register(Feedback)
cip_admin.register(Profile)
cip_admin.register(Notification)
cip_admin.register(VehicleMake)
cip_admin.register(VehicleModel)
cip_admin.register(Payment)
