import inspect


# Core interfacing: C#/PHP-style contracts checked at class-def time.
# Extend Interface on I* types in future.interfaces; app code extends those I* types.


class Interface:
    __strict__ = False

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls is Interface:
            return
        required = {}
        strict = False
        for base in cls.__mro__[1:]:
            if base is Interface or not issubclass(base, Interface):
                continue
            if base.__dict__.get("__strict__", False):
                strict = True
            for name, value in base.__dict__.items():
                if name == "__init__" or not callable(value) or name.startswith("_"):
                    continue
                if not Interface._is_stub(value):
                    continue
                if name not in required:
                    required[name] = inspect.signature(value)
        if not required:
            return
        implemented = {}
        missing = set()
        for name in required:
            for base in cls.__mro__:
                if base is object:
                    continue
                value = getattr(base, name, None)
                if value is None or not callable(value) or name not in base.__dict__:
                    continue
                if base is not cls and issubclass(base, Interface) and Interface._is_stub(value):
                    continue
                implemented[name] = inspect.signature(value)
                break
            else:
                missing.add(name)
        if missing:
            raise TypeError(f"{cls.__name__} must implement: {', '.join(sorted(missing))}")
        for method in required:
            if implemented[method] != required[method]:
                raise TypeError(f"{cls.__name__}.{method}{implemented[method]} does not match interface {required[method]}")
        if strict:
            public = {
                name
                for name, value in cls.__dict__.items()
                if callable(value) and not name.startswith("_")
            }
            extra = public - set(required)
            if extra:
                raise TypeError(f"{cls.__name__} contains unsupported methods: {', '.join(sorted(extra))}")

    def _is_stub(value):
        try:
            source = inspect.getsource(value).strip()
        except (OSError, TypeError):
            return False
        lines = [line.strip() for line in source.splitlines() if line.strip() and not line.strip().startswith("#")]
        if lines and (lines[0].startswith("def ") or lines[0].startswith("async def ")):
            lines = lines[1:]
        if not lines:
            return True
        if len(lines) == 1 and lines[0].startswith("raise") and "NotImplementedError" in lines[0]:
            return True
        return False
