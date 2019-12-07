"""klasowe_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from klasowe.views import (
    main_panel,
    login_view,
    add_class,
    password_change_done,
    username_change,
    email_change,
    event_create,
    events_show,
    event_details,
    event_delete,
    years_manage,
    year_delete
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="klasowe/logout.html"), name="logout"),
    path('main-panel/', main_panel, name="main-panel"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="klasowe/password-reset.html"), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='klasowe/password-reset-done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="klasowe/password-reset-confirm.html"), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="klasowe/password-reset-complete.html"), name="password_reset_complete"),
    path('add-class/', add_class, name="add-class"),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='klasowe/password-change.html'), name="password_change"),
    path('password-change/done', password_change_done, name='password_change_done'),
    path('username-change', username_change, name='username_change'),
    path('email-change/', email_change, name='email-change'),
    path('event-create/', event_create, name='event-create'),
    path('events-show/', events_show, name='events-show'),
    path('event-details/', event_details, name='event-details'),
    path('event-delete/<int:event>', event_delete, name='event-delete'),
    path('years-manage', years_manage, name='years-manage'),
    path('year-delete/<int:id>', year_delete, name='year-delete')
]
