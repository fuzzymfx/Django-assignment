import datetime
import build
import google_apis_oauth
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
import requests
import json
import os

GOOGLE_CLIENT_SECRET_PATH = os.path.join(os.getcwd(), 'client_secrets.json')

GOOGLE_CLIENT_SECRET = json.loads(os.getenv('GOOGLE_CLIENT_SECRET'))
GOOGLE_CLIENT_ID = GOOGLE_CLIENT_SECRET["web"]["client_id"]
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = 'https://fuzzymfx-ominous-bassoon-xxx7rpwpgvwf64gj-8000.preview.app.github.dev/rest/v1/calendar/redirect/'


def home(request):
    return render(request, 'home.html')


def GoogleCalendarInitView(request):
    return redirect(google_apis_oauth.get_authorization_url(
        GOOGLE_CLIENT_SECRET_PATH,
        SCOPES,
        REDIRECT_URI)
    )


def GoogleCalendarRedirectView(request):

    try:
        # print(request)
        # print(request.GET.get('code'))

        credentials = google_apis_oauth.get_crendentials_from_callback(
            request,
            GOOGLE_CLIENT_SECRET_PATH,
            SCOPES,
            REDIRECT_URI
        )
        token = google_apis_oauth.stringify_credentials(credentials)

        creds = google_apis_oauth.load_credentials(token)
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get(
                'dateTime', event['start'].get('date'))
            print(start, event['summary'])
    except Exception as e:
        print(e)
        return HttpResponse('Error')
