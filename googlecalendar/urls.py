from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView

app_name = 'googlecalendar'

urlpatterns = [
    path('rest/v1/calendar/redirect/',
         GoogleCalendarInitView, name='calendar-init'),
    path('rest/v1/calendar/redirect/',
         GoogleCalendarRedirectView,
         name='calendar-redirect'),
]
