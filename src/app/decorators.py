from functools import wraps
from django.http import HttpResponseRedirect, HttpResponseForbidden


def require_session(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'host' not in request.session or 'username' not in request.session or 'password' not in request.session:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponseForbidden
            return HttpResponseRedirect('/login')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
