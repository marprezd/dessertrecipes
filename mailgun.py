# mailgun.py file

# Import the necessary package and module
import requests


class MailgunApi:

    # API_URL provided by Mailgun
    API_URL = 'https://api.mailgun.net/v3/{}/messages'

    def __init__(self, domain, api_key):
        """Define method for initialize the attributes"""
        self.domain = domain
        self.key = api_key
        self.base_url = self.API_URL.format(self.domain)

    def send_email(self, to, subject, text, html=None):
        """Sending out emails using the Mailgun API"""
        if not isinstance(to, (list, tuple)):
            to = [to, ]

        data = {
            'from': 'DessertRecipe <no-reply@{}>'.format(self.domain),
            'to': to,
            'subject': subject,
            'text': text,
            'html': html
        }

        response = requests.post(
            url=self.base_url, auth=('api', self.key), data=data)

        return response
