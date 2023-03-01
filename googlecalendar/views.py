from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import os

GOOGLE_CLIENT_SECRET = json.loads(os.getenv('GOOGLE_CLIENT_SECRET'))


class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri=request.build_absolute_uri(
                reverse('googlecalendar:calendar-redirect')))
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        request.session['google_auth_state'] = state
        return redirect("authorization_url")


class GoogleCalendarRedirectView(View):
    def get(self, request, *args, **kwargs):
        # Verify the state parameter
        if 'google_auth_state' not in request.session or \
                request.GET.get('state') != request.session['google_auth_state']:
            return render(request, 'googlecalendar/error.html',
                          {'error': 'Invalid state parameter'})

        # Get the authorization code from the request
        code = request.GET.get('code')

        # Exchange the authorization code for a token
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar'],
            redirect_uri=request.build_absolute_uri(
                reverse('googlecalendar:calendar-redirect')))
        flow.fetch_token(code=code)

        # Save the credentials in the session
        credentials = flow.credentials
        request.session['google_credentials'] = credentials.to_json()

        # Use the credentials to get the list of events in the user's primary calendar
        try:
            service = build('calendar', 'v3', credentials=credentials)
            events_result = service.events().list(
                calendarId='primary',
                timeMin='now',
                maxResults=10,
                singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])
            return render(request, 'googlecalendar/calendar.html',
                          {'events': events})
        except HttpError as error:
            return render(request, 'googlecalendar/error.html',
                          {'error': f'An error occurred: {error}'})
