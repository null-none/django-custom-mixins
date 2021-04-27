django-custom-mixins
====================

List custom mixins for projects

=======
Install
=======

.. code-block:: bash

    pip install django-custom-mixins


=======
Example
=======

.. code-block:: python
    from django.views.generic import TemplateView
    from django_custom_mixins.mixins import LoginRequiredMixin

    class TestView(LoginRequiredMixin, TemplateView):
        template_name = "test.html"


=======
Mixins
=======

-  AjaxOnlyViewMixin
-  NeverCacheMixin
-  LoginRequiredMixin
-  CSRFExemptMixin
-  CacheMixin
-  CacheControlMixin
-  PaginatorMixin
-  CSVAdmin
-  GetRequestMixin
-  DisableCsrfCheck
-  TimezoneMiddleware
-  ModelDiffMixin
-  ModelAdminRequestMixin
-  CORSMiddleware

=======
Donation
=======

.. image:: https://img.shields.io/badge/Donate-PayPal-green.svg
  :target: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YYZQ6ZRZ3EW5C

=======
License
=======

MIT
