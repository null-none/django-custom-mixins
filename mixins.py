from __future__ import unicode_literals


from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class AjaxOnlyViewMixin(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super(AjaxOnlyViewMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('auth_login'))
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
