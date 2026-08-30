"""
OpenID Connect authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class OpenIdConnectAuthentication(IAuthentication):
    auth_type = "oidc"
