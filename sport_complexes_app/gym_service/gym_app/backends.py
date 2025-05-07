from django.contrib.auth.backends import BaseBackend
import requests
import logging

logger = logging.getLogger(__name__)

class AuthServiceBackend(BaseBackend):
   def authenticate(self, request, username=None, password=None, **kwargs):
       try:
           response = requests.post(
               'http://localhost:8000/api/login/',
               data={'username': username, 'password': password},
               timeout=5
           )
           if response.status_code == 200:
               user_data = response.json()
               request.session['user_data'] = user_data
               return self._create_user(user_data)
           logger.debug(f"Authentication failed for {username}: {response.status_code}")
       except requests.RequestException as e:
           logger.error(f"Auth service error: {e}")
       return None

   def get_user(self, user_id):
       user_data = getattr(self.request, 'session', {}).get('user_data')
       if user_data and user_data['username'] == user_id:
           return self._create_user(user_data)
       return None

   def _create_user(self, user_data):
       class User:
           def __init__(self, data):
               self.username = data['username']
               self.user_role = data['user_role']
               self.permissions = data['permissions']
               self.is_authenticated = True
               self.is_active = True
               self.is_anonymous = False
               self.id = data['username']

           def has_perm(self, perm, obj=None):
               logger.debug(f"Checking permission {perm} for {self.username}: {perm in self.permissions}")
               return perm in self.permissions

           def has_perms(self, perm_list, obj=None):
               return all(self.has_perm(perm, obj) for perm in perm_list)

           def get_all_permissions(self, obj=None):
               return set(self.permissions)

           def get_username(self):
               return self.username

       return User(user_data)

   def set_request(self, request):
       self.request = request