import bottle
import json

from shared_modules import config

class AuthManager:
    def __init__(self, cfg: config.Config):
        self.cfg = cfg

    def get_user_password(self) -> str|None:
        password = bottle.request.headers.get("Authorization")
        
        bearer_prefix = "Bearer "
        if password and password.startswith(bearer_prefix):
            return password[len(bearer_prefix):]
        return None

    def is_authenticated(self) -> bool:
        password = self.get_user_password()
        if password is None:
            return False

        return password == self.cfg.web_server.password

    def requires_password(self):
        return self.cfg.web_server.password_set
    
    def raise_if_not_authenticated(self):
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
