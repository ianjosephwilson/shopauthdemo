"""
Application implementation code.
"""
import logging
import os
import os.path

from zope.sqlalchemy import mark_changed
from shopauth import ShopAuthService, ShopSessionSerializer, ShopAuthConfig
from shopauth.web.pyramid_shim import PyramidWebShimConfig, PyramidWebShim
from shopauth.storage.sqlalchemy_shim import SqlalchemyStorageShim
from shopauth.cookieserializer import get_default_signed_serializer

from .model import ShopSession


logger = logging.getLogger(__name__)


def auth(request):
    # Lib takes over.
    return request.shopauth.begin_auth()


def auth_toplevel(request):
    # Lib takes over.
    return request.shopauth.auth_toplevel()


def auth_callback(request):
    # Lib takes over.
    return request.shopauth.auth_callback()


def api_shop(request):
    """
    Make a test graphql query to get the shop's name.
    """
    # Should be an auth session.
    auth_session, error_response = request.shopauth.verify_api_access()
    if error_response:
        return error_response
    return request.shopauth.test_access(auth_session)


def home(request):
    # Either an auth session or an install session.
    session, error_response = request.shopauth.verify_page_access()
    if error_response:
        return error_response

    # Set the frame restricting headers.
    # This prevents our frame from being framed without our permission.
    request.shopauth.set_app_headers()

    # We reach into the config here because this is just a demo.
    # hopefully your app would already be embedded or not.
    if request.shopauth.config.embedded:
        index = "client/embedded_index.html"
    else:
        index = "client/standalone_index.html"
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), index)
    with open(
        template_path,
        "r",
    ) as f:
        content = f.read()
        import json

        # @TODO We should clearly do something different here.
        content = content.replace(
            "{config_json_str}",
            json.dumps({"apiKey": request.shopauth.config.api_key}),
        )
    response = request.response
    response.text = content
    response.content_type = "text/html"
    return response


def clean_csv(csv):
    if not csv or not csv.strip():
        return []
    else:
        return [part.strip() for part in csv.split(",") if part.strip()]


def includeme(config):

    config.add_route("auth", "/auth")
    config.add_route("auth-toplevel", "/auth/toplevel")
    config.add_route("auth-callback", "/auth/callback")
    config.add_route("home", "/")
    config.add_route("api-shop", "/api/shop")
    config.add_route("pages", "/pages/{url}")
    config.add_view(auth, route_name="auth")
    config.add_view(auth_toplevel, route_name="auth-toplevel")
    config.add_view(auth_callback, route_name="auth-callback")
    config.add_view(home, route_name="home")
    # Have all other pages also load the home-page skeleton.
    config.add_view(home, route_name="pages")
    config.add_view(api_shop, route_name="api-shop", renderer="json")

    def shopauth_factory(request):
        pyramid_shim_config = PyramidWebShimConfig(
            auth_route="auth",
            auth_toplevel_route="auth-toplevel",
            auth_callback_route="auth-callback",
            webhook_uninstall_route="webhook-uninstall",
            cookie_secret=os.environ.get("SHOPIFY_COOKIE_SECRET"),
            home_route="home",
        )
        shopauth_config = ShopAuthConfig(
            oauth_cookie_name="shopify_oauth",
            auth_cookie_name="shopify_auth",
            api_key=os.environ.get("SHOPIFY_API_KEY"),
            api_version=os.environ.get("SHOPIFY_API_VERSION"),
            api_secret=os.environ.get("SHOPIFY_API_SECRET"),
            embedded=True,
            need_offline_access_token=True,
            need_online_access_token=True,
            access_scopes=clean_csv(os.environ.get("SHOPIFY_ACCESS_SCOPES")),
            jwt_leeway_in_seconds=5,
            toplevel_cookie_name="shopify_toplevel",
        )
        storage_shim = SqlalchemyStorageShim(
            db=request.db,
            table=ShopSession.__table__,
            serializer=ShopSessionSerializer(),
            mark_changed=mark_changed,
        )
        web_shim = PyramidWebShim(
            config=pyramid_shim_config,
            signed_serializer=get_default_signed_serializer,
            request=request,
        )
        return ShopAuthService(
            config=shopauth_config,
            web_shim=web_shim,
            storage_shim=storage_shim,
        )

    config.add_request_method(shopauth_factory, "shopauth", reify=True)
