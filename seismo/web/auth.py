"""
Authentication manager for the web server.
"""

import bottle
import json
import time
from collections import defaultdict

from seismo import config

class AuthManager:
    """
    Manages authentication for the web server with rate limiting.
    
    Uses Bearer token authentication and tracks failed attempts per IP address.
    """
    
    def __init__(self, cfg: config.Config):
        self.cfg = cfg

    def get_user_password(self) -> str|None:
        """
        Extract password from Authorization header. Supports Bearer 
        token format.
        """

        password = bottle.request.headers.get("Authorization")
        
        bearer_prefix = "Bearer "
        if password and password.startswith(bearer_prefix):
            return password[len(bearer_prefix):]
        return None

    def is_authenticated(self) -> bool:
        """
        Check if the current request is authenticated.
        """
        
        password = self.get_user_password()
        if password is None:
            return False

        return password == self.cfg.web_server.password

    def requires_password(self) -> bool:
        """
        Check if password authentication is required.
        """
        return self.cfg.web_server.password_set
    
    def raise_if_not_authenticated(self):
        """
        Raise bottle.HTTPError 401 if not authenticated.
        """

        if not self.requires_password():
            return
        
        password = self.get_user_password()
        if password is None:
            bottle.abort(400, json.dumps({
                "error": "password is required to access this page",
            }))
        
        if not self.is_authenticated():
            bottle.abort(401, json.dumps({
                "error": "not authorized", 
            }))
