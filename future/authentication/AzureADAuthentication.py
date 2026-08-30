"""
Azure AD authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class AzureADAuthentication(IAuthentication):
    auth_type = "basic"
