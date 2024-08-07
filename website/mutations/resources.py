from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.fields import Field

from mutations import models


class MutationResource(resources.ModelResource):

    ATTRIBUTE_CUSTOMER_NAME = "customer_name"
    ATTRIBUTE_CUSTOMER_UPHANCE_ID = "customer_uphance_id"
    ATTRIBUTE_CUSTOMER_SNELSTART_ID = "customer_snelstart_id"

    def __init__(self, **kwargs):
        """Initialize by creating a field for each content type that is supported."""
        super(MutationResource, self).__init__(**kwargs)
        self.added_content_type_fields = dict()
        self.customer_type = ContentType.objects.get(app_label="customers", model="customer")
        self._invoice_type = ContentType.objects.get(app_label="invoices", model="invoice")
        self._credit_note_type = ContentType.objects.get(app_label="credit_notes", model="creditnote")
        self._pick_ticket_type = ContentType.objects.get(app_label="pick_tickets", model="pickticket")

    def before_export(self, queryset, *args, **kwargs):
        """Initialize by creating a field for content type that is supported."""
        for obj in queryset:
            if obj.content_type == self.customer_type:
                self.fields[self.ATTRIBUTE_CUSTOMER_NAME] = Field(
                    column_name=f"Customer name", attribute=self.ATTRIBUTE_CUSTOMER_NAME, readonly=True
                )
                self.fields[self.ATTRIBUTE_CUSTOMER_UPHANCE_ID] = Field(
                    column_name=f"Customer Uphance ID", attribute=self.ATTRIBUTE_CUSTOMER_UPHANCE_ID, readonly=True
                )
                self.fields[self.ATTRIBUTE_CUSTOMER_SNELSTART_ID] = Field(
                    column_name=f"Customer Snelstart ID", attribute=self.ATTRIBUTE_CUSTOMER_SNELSTART_ID, readonly=True
                )

    def export_customer_field(self, field, obj):
        """Export the custom customer fields."""
        if obj.content_type == self.customer_type:
            if field.attribute == self.ATTRIBUTE_CUSTOMER_NAME:
                return obj.on.uphance_name
            elif field.attribute == self.ATTRIBUTE_CUSTOMER_UPHANCE_ID:
                return obj.on.uphance_id
            elif field.attribute == self.ATTRIBUTE_CUSTOMER_SNELSTART_ID:
                return obj.on.snelstart_id

        return None

    def export_field(self, field, obj):
        """Check for added product field before exporting."""
        if field.attribute in [
            self.ATTRIBUTE_CUSTOMER_NAME,
            self.ATTRIBUTE_CUSTOMER_UPHANCE_ID,
            self.ATTRIBUTE_CUSTOMER_SNELSTART_ID,
        ]:
            return self.export_customer_field(field, obj)
        else:
            return super(MutationResource, self).export_field(field, obj)

    class Meta:
        """Meta class."""

        model = models.Mutation
        fields = [
            "id",
            "created",
            "method",
            "trigger",
            "success",
            "message",
        ]
        export_order = [
            "id",
            "created",
            "method",
            "trigger",
            "success",
            "message",
        ]
