from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class InvoiceCreateUpdateDeleteApiView(APIView):

    def check_permissions(self, request):
        expected_secret = settings.UPHANCE_SECRET
        if expected_secret is None:
            return True

        request_secret = request.GET.get("secret", None)
        if request_secret is None or request_secret != expected_secret:
            return False

        return True

    def _create_invoice(self, invoice: dict):
        pass

    def _delete_invoice(self, invoice: dict):
        pass

    def _update_invoice(self, invoice: dict):
        pass

    def post(self, request):
        event = request.data.get("event", None)
        if event is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        invoice = request.data.get("invoice", None)
        if invoice is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event == "invoice_create":
            self._create_invoice(invoice)
        elif event == "invoice_update":
            self._update_invoice(invoice)
        elif event == "invoice_delete":
            self._delete_invoice(invoice)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
