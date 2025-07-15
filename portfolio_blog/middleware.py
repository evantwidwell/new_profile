from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class WWWRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to redirect www.evantwidwell.com to evantwidwell.com
    """
    def process_request(self, request):
        host = request.get_host()
        if host == 'www.evantwidwell.com':
            new_url = f"https://evantwidwell.com{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)
        return None
