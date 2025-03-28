# ✨ Future ✨
Next Gen. [ASGI](https://github.com/django/asgiref) Framework for minimal Web APIs
- [ASGI](https://asgi.readthedocs.io/)
- [ASGI GitHub](https://github.com/django/asgiref)
- [ASGI Fundamentals](https://www.youtube.com/watch?v=ai7y--6ElAE&list=PLJ_usHaf3fgO_PgB1zTSlKVSqDdvh49bi)

## Build Status
<a href="https://github.com/Defendinary/future/actions"><img src="https://github.com/Defendinary/future/workflows/Test%20Suite/badge.svg" alt="Build Status"></a>
<a href="https://pypi.org/project/future-api/"><img src="https://badge.fury.io/py/star.svg" alt="Package version"></a>


# Known bugs
- Subdomain clobbering since only partial domain is checked. Should probably use full domain in route dictionary.


# Usage
```shell
$ poetry init myproject
$ poetry shell

# https://stackoverflow.com/questions/4830856/is-it-possible-to-use-pip-to-install-a-package-from-a-private-github-repository
# https://github.com/settings/tokens?type=beta
$ GH_TOKEN="TOKEN" echo "https://${GH_TOKEN}:@github.com" > ${HOME}/.git-credentials && git config --global credential.helper store
$ poetry add git+ssh://git@github.com/Defendinary/future.git@master
#$ poetry add future-api # when released to the public..!
$ poetry install

# Scaffold default, nice & clean application structure based on future-broilerplate
$ future new .

# Create new controller
$ future controller TestController

# Create new middleware
$ future middleware TestMiddleware

# Create new model
$ future model TestModel

# Print all routes
$ future routes

# Run app
$ future run

# Install Authentication
$ future install SSOAuthentication
$ future install SAMLAuthentication
$ future install BasicAuthentication

# Install custom Middlewares
$ future install ResponseCodeConfuser
$ future install SQLiResponseConfuser
```