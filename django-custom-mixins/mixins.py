from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.utils.cache import patch_response_headers
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from django.contrib import admin


class CSVAdmin(admin.ModelAdmin):
    """
    Adds a CSV export action to an admin view.
    """

    # This is the maximum number of records that will be written.
    # Exporting massive numbers of records should be done asynchronously.
    csv_record_limit = 1000

    extra_csv_fields = ()

    def get_actions(self, request):
        actions = self.actions if hasattr(self, 'actions') else []
        actions.append('csv_export')
        actions = super(CSVAdmin, self).get_actions(request)
        return actions

    def get_extra_csv_fields(self, request):
        return self.extra_csv_fields

    def csv_export(self, request, qs=None, *args, **kwargs):
        import csv
        from django.http import HttpResponse
        from django.template.defaultfilters import slugify

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' \
            % slugify(self.model.__name__)
        headers = list(self.list_display) + list(self.get_extra_csv_fields(request))
        writer = csv.DictWriter(response, headers)

        # Write header.
        header_data = {}
        for name in headers:
            if hasattr(self, name) \
            and hasattr(getattr(self, name), 'short_description'):
                header_data[name] = getattr(
                    getattr(self, name), 'short_description')
            else:
                field = self.model._meta.get_field_by_name(name)
                if field and field[0].verbose_name:
                    header_data[name] = field[0].verbose_name
                else:
                    header_data[name] = name
            header_data[name] = header_data[name].title()
        writer.writerow(header_data)

        # Write records.
        for r in qs[:self.csv_record_limit]:
            data = {}
            for name in headers:
                if hasattr(r, name):
                    data[name] = getattr(r, name)
                elif hasattr(self, name):
                    data[name] = getattr(self, name)(r)
                else:
                    raise Exception, 'Unknown field: %s' % (name,)

                if callable(data[name]):
                    data[name] = data[name]()
            writer.writerow(data)
        return response
    csv_export.short_description = \
        'Exported selected %(verbose_name_plural)s as CSV'

class PaginatorMixin(object):
    def __init__(self, queryset, numb_pages, request_page):
        self.queryset       = queryset          #egg: models.Post.objects.all()
        self.numb_pages     = numb_pages        #egg: int 10 `is number per page`
        self.request_page   = request_page      #egg: request.GET.get('page')

    def page_numbering(self):
        paginator = Paginator(self.queryset, self.numb_pages)
        try:
            pagination = paginator.page(self.request_page)
        except PageNotAnInteger:
            pagination = paginator.page(1)
        except EmptyPage:
            pagination = paginator.page(paginator.num_pages)

        index       = pagination.number - 1
        limit       = 5 #limit for show range left and right of number pages
        max_index   = len(paginator.page_range)
        start_index = index - limit if index >= limit else 0
        end_index   = index + limit if index <= max_index - limit else max_index

        page_range  = list(paginator.page_range)[start_index:end_index]
        return page_range

    def queryset_paginated(self):
        paginator = Paginator(self.queryset, self.numb_pages)
        try:
            queryset_paginated = paginator.page(self.request_page)
        except PageNotAnInteger:
            queryset_paginated = paginator.page(1)
        except EmptyPage:
            queryset_paginated = paginator.page(paginator.num_pages)

        return queryset_paginated


class AjaxOnlyViewMixin(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super(AjaxOnlyViewMixin, self).dispatch(request, *args, **kwargs)


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class CacheControlMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        response = super(CacheControlMixin, self).dispatch(*args, **kwargs)
        patch_response_headers(response, self.get_cache_timeout())
        return response
