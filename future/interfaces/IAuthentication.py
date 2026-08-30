from future.interfacing import Interface


class IAuthentication(Interface):
    auth_type: str = ""
