"""
Regular username & password authentication (check against SQL database, generating a JWT).
"""

from future.interfaces.IAuthentication import IAuthentication


class BasicAuthentication(IAuthentication):
    auth_type = "basic"
