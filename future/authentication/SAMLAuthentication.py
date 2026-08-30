"""
SAML Single Sign-On authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class SAMLAuthentication(IAuthentication):
    auth_type = "sso"
