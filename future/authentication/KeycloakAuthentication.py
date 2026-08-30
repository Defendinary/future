"""
Keycloak authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class KeycloakAuthentication(IAuthentication):
    auth_type = "oauth"
