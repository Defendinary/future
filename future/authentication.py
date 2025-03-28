"""
from blacksheep import Application

from app.settings import Settings

def configure_authentication(app: Application, settings: Settings):
    \"""
    Configure authentication as desired. For reference:
    https://www.neoteroi.dev/blacksheep/authentication/
    \"""
    
"""

class Authentication:
    auth_type = None


class UserPass(Authentication):
    # Regular username & password authentication, check against SQL database, generating a JWT
    auth_type = "userpass"


class SSO(Authentication):
    # SSO / SAML authentication
    auth_type = "sso"


class Kerberos(Authentication):
    # Kerberos authentication
    auth_type = "kerberos"


class AzureAD(Authentication):
    # Azure AD authentication
    auth_type = "azuread"


class OAuth(Authentication):
    # OAuth authentication
    auth_type = "oauth"


