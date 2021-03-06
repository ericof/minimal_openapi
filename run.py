"""A very simple API example app showcasing the power of pyramid_openapi3."""

from dataclasses import dataclass
from openapi_core.schema.exceptions import OpenAPIMappingError
from pyramid.config import Configurator
from pyramid.httpexceptions import exception_response
from pyramid.view import view_config
from wsgiref.simple_server import make_server


@dataclass
class Item:
    """A single TODO item."""

    title: str

    def __json__(self, request):
        """How should this object look in the JSON response?"""
        return {"title": self.title}


# fmt: off
ITEMS = [
    Item(title="Buy milk"),
]
# fmt: on


@view_config(route_name="todo", renderer="json", request_method="GET", openapi=True)
def get(request):
    return ITEMS


@view_config(route_name="todo", renderer="json", request_method="POST", openapi=True)
def post(request):
    item = Item(title=request.openapi_validated.body.title)
    ITEMS.append(item)
    return "Added."


def app():
    with Configurator() as config:
        config.include("pyramid_openapi3")
        config.pyramid_openapi3_spec("openapi.yaml", route="/api/v1/openapi.yaml")
        config.pyramid_openapi3_validation_error_view("openapi_validation_error")
        config.pyramid_openapi3_add_explorer(route="/api/v1/")
        config.add_route("todo", "/api/v1/todo/")
        config.scan()
        return config.make_wsgi_app()


if __name__ == "__main__":
    server = make_server("0.0.0.0", 8080, app())
    server.serve_forever()


# TODO: could this be moved to pyramid_openapi3 package?
def extract_error(err):
    if isinstance(getattr(err, "original_exception", None), OpenAPIMappingError):
        return extract_error(err.original_exception)
    return err.msg


@view_config(name="openapi_validation_error")
def openapi_validation_error(context, request):
    errors = [str(err) for err in request.openapi_validated.errors]
    return exception_response(400, json_body=errors)
