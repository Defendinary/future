"""
Auth0 authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class Auth0Authentication(IAuthentication):
    auth_type = "oauth"
