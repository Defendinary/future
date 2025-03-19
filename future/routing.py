from typing import Any, Callable, Optional, TypedDict
from future.middleware import Middleware
import re


class RegexConfig(TypedDict):
    paths: list[re.Pattern]


class RouteException(Exception):
    pass


class InvalidValuePatternName(RouteException):
    def __init__(self, pattern_name: str, matched_parameter: str):
        self.pattern_name = pattern_name
        self.matched_parameter = matched_parameter
        super().__init__(f"Invalid value pattern name: {pattern_name} in {matched_parameter}")


class RouteMatch:
    def __init__(self, route: 'Route', params: Optional[dict[str, str]]):
        self.route = route
        self.params = params


class Route:
    value_patterns = {
        "string": r"[^\/]+",
        "str": r"[^\/]+",
        "path": r".*",
        "int": r"\d+",
        "float": r"\d+(?:\.\d+)?",
        "uuid": r"[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}",
    }

    def __init__(
        self,
        methods: list[str],
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        self.methods = methods
        self.path = path
        self.endpoint = endpoint
        self.name = name
        self.strict_slashes = strict_slashes
        self.middlewares = middlewares or []

    def compile_pattern(self) -> None:        
        _route_all_rx = re.compile(b"\\*")
        _route_param_rx = re.compile(b"/:([^/]+)")
        
        _mustache_route_param_rx = re.compile(b"/{([^}]+)}")
        _angle_bracket_route_param_rx = re.compile(b"/<([^>]+)>")

        _named_group_rx = re.compile(b"\\?P<([^>]+)>")
        _escaped_chars = {
            b".",
            b"[",
            b"]",
            b"(",
            b")",
        }

        def _get_parameter_pattern_fragment(name: str, pattern: Optional[str] = None) -> bytes:
            if pattern is None:
                pattern = Route.value_patterns["string"]
            return rb"/(?P<" + name.encode() + rb">" + pattern.encode() + rb")"

        def _handle_rich_parameter(match: re.Match) -> bytes:
            matched_parameter = next(iter(match.groups()))
            assert isinstance(matched_parameter, bytes)

            if b":" in matched_parameter:
                raw_pattern_name, parameter_name = matched_parameter.split(b":")
                parameter_pattern_name = raw_pattern_name.decode()
                parameter_pattern = Route.value_patterns.get(parameter_pattern_name)
                
                if not parameter_pattern:
                    raise InvalidValuePatternName(parameter_pattern_name, matched_parameter.decode("utf8"))

                return _get_parameter_pattern_fragment(parameter_name.decode(), parameter_pattern)
            
            return _get_parameter_pattern_fragment(matched_parameter.decode())


        pattern = self.path.encode()
        for c in _escaped_chars:
            if c in pattern:
                pattern = pattern.replace(c, b"\\" + c)


        if b"*" in pattern:
            if pattern.count(b"*") > 1:
                raise RouteException("A route pattern cannot contain more than one star sign *.")
            if b"/*" in pattern:
                pattern = _route_all_rx.sub(rb"?(?P<tail>.*)", pattern)
            else:
                pattern = _route_all_rx.sub(rb"(?P<tail>.*)", pattern)


        if b"<" in pattern:
            pattern = _angle_bracket_route_param_rx.sub(_handle_rich_parameter, pattern)

        if b"{" in pattern:
            pattern = _mustache_route_param_rx.sub(_handle_rich_parameter, pattern)

        if b"/:" in pattern:
            pattern = _route_param_rx.sub(rb"/(?P<\1>[^\/]+)", pattern)


        param_names = []
        for p in _named_group_rx.finditer(pattern):
            param_name = p.group(1).decode()
            
            if param_name in param_names:
                raise ValueError(f"cannot have multiple parameters with name: {param_name}")
            
            param_names.append(param_name)


        if len(pattern) > 1 and not pattern.endswith(b"*"):
            pattern = pattern + b"/?"


        self._rx = re.compile(b"^" + pattern + b"$", re.IGNORECASE)
        self.param_names = param_names


    def match(self, request_path: bytes) -> Optional[RouteMatch]:
        #print("Matching on reqpath:", request_path, "using regex:", self._rx)
        match = self._rx.match(request_path)
        if not match:
            return None
        
        lol = RouteMatch(self, match.groupdict() if self.param_names else None)
        return lol



class Get(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["GET"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Post(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["POST"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Put(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["PUT"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Head(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["HEAD"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Options(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["OPTIONS"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Patch(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["PATCH"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class Delete(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: str,
        strict_slashes: bool = False,
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        super().__init__(
            methods=["DELETE"],
            path=path,
            endpoint=endpoint,
            name=name,
            strict_slashes=strict_slashes,
            middlewares=middlewares,
        )


class RouteGroup:
    def __init__(
        self,
        routes: list[Route],
        name: str = "",
        prefix: str = "",
        subdomain: str = "",
        middlewares: Optional[list[Middleware]] = None,
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.routes = routes
        self.subdomain = subdomain
        self.middlewares = middlewares or []

class EndpointConfig(TypedDict):
    middleware_before: list[Middleware]
    middleware_after: list[Middleware]
    route: Route



'''
class BlacksheepRoute:
    __slots__ = (
        "handler",
        "pattern",
        "param_names",
        "_rx",
    )

    pattern: bytes

    value_patterns = {
        "string": r"[^\/]+",
        "str": r"[^\/]+",
        "path": r".*",
        "int": r"\d+",
        "float": r"\d+(?:\.\d+)?",
        "uuid": r"[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]"
        + r"{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}",
    }

    def __init__(
        self,
        pattern: Union[str, bytes],
        handler: Any,
    ):
        raw_pattern = self.normalize_pattern(pattern)
        self.handler = handler
        self.pattern = raw_pattern
        rx, param_names = self._get_regex_for_pattern(raw_pattern)
        self._rx = rx
        self.param_names = [name.decode("utf8") for name in param_names]

    @property
    def rx(self) -> re.Pattern:
        return self._rx

    @property
    def has_params(self) -> bool:
        return self._rx.groups > 0

    def _get_regex_for_pattern(self, pattern: bytes):
        """
        Converts a raw pattern into a compiled regular expression that can be used
        to match bytes URL paths, extracting route parameters.
        """
        # TODO: should blacksheep support ":" in routes (using escape chars)?
        for c in _escaped_chars:
            if c in pattern:
                pattern = pattern.replace(c, b"\\" + c)

        if b"*" in pattern:
            # throw exception if a star appears more than once
            if pattern.count(b"*") > 1:
                raise RouteException(
                    "A route pattern cannot contain more than one star sign *. "
                    "Multiple star signs are not supported."
                )

            if b"/*" in pattern:
                pattern = _route_all_rx.sub(rb"?(?P<tail>.*)", pattern)
            else:
                pattern = _route_all_rx.sub(rb"(?P<tail>.*)", pattern)

        # support for < > patterns, e.g. /api/cats/<cat_id>
        # but also: /api/cats/<int:cat_id> or /api/cats/<uuid:cat_id> for more
        # granular control on the generated pattern
        if b"<" in pattern:
            pattern = _angle_bracket_route_param_rx.sub(
                self._handle_rich_parameter, pattern
            )

        # support for mustache patterns, e.g. /api/cats/{cat_id}
        # but also: /api/cats/{int:cat_id} or /api/cats/{uuid:cat_id} for more
        # granular control on the generated pattern
        if b"{" in pattern:
            pattern = _mustache_route_param_rx.sub(self._handle_rich_parameter, pattern)

        # route parameters defined using /:name syntax
        if b"/:" in pattern:
            pattern = _route_param_rx.sub(rb"/(?P<\1>[^\/]+)", pattern)

        # NB: following code is just to throw user friendly errors;
        # regex would fail anyway, but with a more complex message
        # 'sre_constants.error: redefinition of group name'
        # we only return param names as they are useful for other things
        param_names = []
        for p in _named_group_rx.finditer(pattern):
            param_name = p.group(1)
            if param_name in param_names:
                raise ValueError(
                    f"cannot have multiple parameters with name: " f"{param_name}"
                )

            param_names.append(param_name)

        if len(pattern) > 1 and not pattern.endswith(b"*"):
            # NB: the /? at the end ensures that a route is matched both with
            # a trailing slash or not
            pattern = pattern + b"/?"
        return re.compile(b"^" + pattern + b"$", re.IGNORECASE), param_names

    def _handle_rich_parameter(self, match: re.Match):
        """
        Handles a route parameter that can include details about the pattern,
        for example:

        /api/cats/<int:cat_id>
        /api/cats/<uuid:cat_id>

        /api/cats/{int:cat_id}
        /api/cats/{uuid:cat_id}
        """
        assert (
            len(match.groups()) == 1
        ), "The regex using this function must handle a single group at a time."

        matched_parameter = next(iter(match.groups()))
        assert isinstance(matched_parameter, bytes)

        if b":" in matched_parameter:
            assert matched_parameter.count(b":") == 1

            raw_pattern_name, parameter_name = matched_parameter.split(b":")
            parameter_pattern_name = raw_pattern_name.decode()
            parameter_pattern = Route.value_patterns.get(parameter_pattern_name)

            if not parameter_pattern:
                raise InvalidValuePatternName(
                    parameter_pattern_name,
                    matched_parameter.decode("utf8"),
                )

            return _get_parameter_pattern_fragment(
                parameter_name, parameter_pattern.encode()
            )
        return _get_parameter_pattern_fragment(matched_parameter)

    def normalize_pattern(self, pattern: Union[str, bytes]) -> bytes:
        if isinstance(pattern, str):
            raw_pattern = pattern.encode("utf8")
        else:
            raw_pattern = pattern

        if raw_pattern == b"":
            raw_pattern = b"/"
        if len(raw_pattern) > 1 and raw_pattern.endswith(b"/"):
            raw_pattern = raw_pattern.rstrip(b"/")

        return raw_pattern

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.pattern.decode('utf8')}\">"

    @staticmethod
    def _normalize_rich_parameter(match: re.Match):
        matched_parameter = next(iter(match.groups()))
        parts = matched_parameter.split(b":")
        parameter_name = parts[1] if len(parts) > 1 else matched_parameter
        return b"/{" + parameter_name + b"}"

    @property
    def mustache_pattern(self) -> str:
        pattern = self.pattern
        if b"<" in pattern:
            pattern = _angle_bracket_route_param_rx.sub(
                self._normalize_rich_parameter, pattern
            )
        if b"{" in pattern:
            pattern = _mustache_route_param_rx.sub(
                self._normalize_rich_parameter, pattern
            )
        return _route_param_rx.sub(rb"/{\1}", pattern).decode("utf8")

    @property
    def full_pattern(self) -> bytes:
        return self._rx.pattern

    def match(self, request: Request) -> Optional[RouteMatch]:
        return self.match_by_path(ensure_bytes(request._path))

    def match_by_path(self, path: bytes) -> Optional[RouteMatch]:
        """
        Returns a match by path - this method can be used only when the route does not
        define any filter.
        """
        if not self.has_params and path.lower() == self.pattern:
            return RouteMatch(self, None)

        match = self._rx.match(path)

        if not match:
            return None

        return RouteMatch(self, match.groupdict() if self.has_params else None)
'''
