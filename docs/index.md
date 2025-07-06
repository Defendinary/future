# Welcome to Future Framework

**Next Gen. ASGI Framework for minimal Web APIs**

Future is a modern, minimalist ASGI framework designed for building fast, scalable web APIs with zero decorators and maximum clarity.

## 🚀 Quick Start

```bash
# Install Future
poetry add future-api

# Create a new project
future init my-project

# Show all routes
future routes
```

## ✨ Key Features

- **Zero Decorators**: Clean, explicit code without magic
- **Static Methods**: Controller methods without `self` parameters
- **Type Safety**: Comprehensive type annotations throughout
- **WebSocket Support**: Native WebSocket routing
- **GraphQL Integration**: Built-in Strawberry GraphQL support
- **CLI Tool**: Complete project management with `future` command
- **Middleware System**: Hierarchical request/response interception
- **Cron Scheduler**: Built-in cron-like task scheduling

## 📖 Documentation

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [Controllers](controllers.md)
- [Routing](routing.md)
- [Middleware](middleware.md)
- [WebSockets](websockets.md)
- [GraphQL](graphql.md)
- [CLI Tool](cli.md)
- [Configuration](configuration.md)

## 🛠️ Development

```bash
# Run tests
poetry run pytest

# Check code quality
poetry run ruff check .
poetry run mypy .

# Build documentation
poetry run mkdocs build
poetry run mkdocs serve
```

## 📦 Installation

```bash
pip install future-api
```

Or with Poetry:

```bash
poetry add future-api
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 