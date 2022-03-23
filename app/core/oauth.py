from abc import abstractmethod

import requests
from authlib.integrations.requests_client import OAuth2Session
from flask import redirect, request, url_for
from transliterate import translit

from app.core import config


class OAuthSignIn:
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = getattr(config.OAuthSettings(), provider_name)
        redirect_uri = f"{config.FlaskSettings.redirect_uri}{provider_name}"
        self.client = OAuth2Session(
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            redirect_uri=redirect_uri,
        )
        self.authorize_url = None

    def authorize(self, state=None):
        url, _ = self.client.create_authorization_url(self.authorize_url, state)
        return redirect(url)

    @abstractmethod
    def callback(self):
        pass

    def get_callback_url(self):
        return url_for("oauth_callback", provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class YandexSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__("yandex")
        self.authorize_url = "https://oauth.yandex.ru/authorize"
        self.access_token_url = "https://oauth.yandex.ru/token"
        self.info_url = "https://login.yandex.ru/info?oauth_token="
        self.client.scope = "login:email"

    def callback(self):
        token = self.client.fetch_token(
            self.access_token_url, authorization_response=request.url
        )
        response = requests.get(f'{self.info_url}{token["access_token"]}')
        info = response.json()

        return info["id"], info["default_email"]


class MailSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__("mail")
        self.authorize_url = "https://oauth.mail.ru/login"
        self.access_token_url = "https://oauth.mail.ru/token"
        self.info_url = "https://oauth.mail.ru/userinfo?access_token="

    def callback(self):
        token = self.client.fetch_token(
            self.access_token_url, authorization_response=request.url
        )
        response = requests.get(f'{self.info_url}{token["access_token"]}')
        info = response.json()
        return info["id"], info["email"]


class VkontakteSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__("vkontakte")
        self.authorize_url = "https://oauth.vk.com/authorize"
        self.access_token_url = "https://oauth.vk.com/access_token"
        self.info_url = "https://api.vk.com/method/users.get?v=5.131&access_token="
        self.client.token_endpoint_auth_method = "client_secret_post"

    def callback(self):
        token = self.client.fetch_token(
            self.access_token_url, authorization_response=request.url
        )
        response = requests.get(
            f'{self.info_url}{token["access_token"]}&user_ids={token["user_id"]}'
        )
        info = response.json()["response"][0]
        login = f'{info["first_name"]}{info["last_name"]}'.lower()
        translit_login = translit(login, "ru", reversed=True)
        email = f"{translit_login}@yandex_auth.test"
        return str(info["id"]), email


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__("google")
        self.authorize_url = "https://accounts.google.com/o/oauth2/auth"
        self.access_token_url = "https://accounts.google.com/o/oauth2/token"
        self.info_url = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token="
        self.client.scope = "openid email profile"

    def callback(self):
        token = self.client.fetch_token(
            self.access_token_url, authorization_response=request.url
        )
        response = requests.get(f'{self.info_url}{token["id_token"]}')
        info = response.json()
        return info["sub"], info["email"]
