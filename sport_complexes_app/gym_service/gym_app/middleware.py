import requests
import logging
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

logger = logging.getLogger(__name__)

class AuthServiceUser(AnonymousUser):
    def __init__(self, username, user_role, permissions):
        self.username = username
        self.user_role = user_role
        self.permissions = permissions or []
        self.is_authenticated = True
        self.is_active = True

    def has_perm(self, perm, obj=None):
        logger.debug(f"Checking permission {perm} for {self.username}: {perm in self.permissions}")
        return perm in self.permissions

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def get_all_permissions(self, obj=None):
        return set(self.permissions)

    def get_username(self):
        return self.username

class AuthServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Якщо користувач уже автентифікований, пропускаємо
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)

        # Перевіряємо сесію
        session_key = request.session.get('sessionid')
        if session_key:
            try:
                # Викликаємо API auth_service для перевірки користувача
                response = requests.get(
                    'http://127.0.0.1:8000/api/user/permissions/',
                    headers={'Cookie': f'sessionid={session_key}'},
                    timeout=5
                )
                if response.status_code == 200:
                    user_data = response.json()
                    request.user = AuthServiceUser(
                        username=user_data['username'],
                        user_role=user_data['role'],
                        permissions=user_data.get('permissions', [])
                    )
                    logger.debug(f"User {request.user.username} authenticated via auth_service")
                else:
                    logger.debug("No valid user data from auth_service")
                    request.user = AnonymousUser()
            except requests.RequestException as e:
                logger.error(f"Auth service error: {e}")
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)