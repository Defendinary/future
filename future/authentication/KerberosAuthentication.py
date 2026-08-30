"""
Kerberos Single Sign-On authentication.
"""

from future.interfaces.IAuthentication import IAuthentication


class KerberosAuthentication(IAuthentication):
    auth_type = "sso"
