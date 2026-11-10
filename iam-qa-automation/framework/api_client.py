"""Employer showcase: one client layer for HTTP, cookies, and consistent test diagnostics.

Tests assert business/security outcomes; the client only encapsulates transport.
Session cookies persist within this client but never leak between test cases.
"""
import requests


class IdentityApi:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'X-IdentityFlow-Demo': '1'})

    def get(self, route: str):
        return self.session.get(f'{self.base_url}/api/{route}', timeout=15)

    def post(self, route: str, payload: dict):
        return self.session.post(f'{self.base_url}/api/{route}', json=payload, timeout=15)

    def login(self, username='alex.viewer', password='DemoPass!2026'):
        return self.post('login', {'username': username, 'password': password})

    def close(self):
        self.session.close()
