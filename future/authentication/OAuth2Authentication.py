"""
OAuth 2 authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class OAuth2Authentication(IAuthentication):
    auth_type = "oauth"
