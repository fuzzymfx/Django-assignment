from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView
from googlecalendar import views

app_name = 'googlecalendar'

urlpatterns = [
    path('', GoogleCalendarInitView.as_view(), name='calendar-init'),
    path('rest/v1/calendar/redirect/',
         GoogleCalendarRedirectView.as_view(),
         name='calendar-redirect'),
    path('authorization/', views.authorization_url, name='authorization_url'),
]
