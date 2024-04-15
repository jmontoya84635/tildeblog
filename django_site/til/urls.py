from django.urls import path
from . import views

app_name = "til"  # this registers the namespace for reverse lookups
urlpatterns = [
    path("edit/<int:learnt_id>", views.learning_data_entry, name="til_de_id"),
    path("add", views.learning_data_entry, name="til_de"),
    path("show/<int:learnt_id>", views.show, name="til_show"),
    path("tagged/", views.landing_page, name="til_show"),
    path("tagged/<str:tagstring>", views.landing_page, name="til_show_tagged"),
    path("", views.landing_page, name="til_landing"),
    path("login", views.login_view, name="til_login"),
    path("signup", views.signup_view, name="til_signup"),
    path("logout", views.logout_view, name="til_logout")
]