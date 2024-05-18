from django.views.generic import RedirectView


class IndexView(RedirectView):
    """
    Index View.

    This view redirects to the administration page.
    """

    url = "/admin"
