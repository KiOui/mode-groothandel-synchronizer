from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.fields import Field

from customers import models
from customers.models import Customer
from mutations.models import Mutation


class CustomerResource(resources.ModelResource):

    ATTRIBUTE_MUTATION_METHOD = "mutation_method"
    ATTRIBUTE_MUTATION_TRIGGER = "mutation_trigger"
    ATTRIBUTE_MUTATION_SUCCESS = "mutation_success"
    ATTRIBUTE_MUTATION_MESSAGE = "mutation_message"

    def __init__(self, **kwargs):
        super(CustomerResource, self).__init__(**kwargs)
        self.content_type = ContentType.objects.get_for_model(Customer)

    def before_export(self, queryset, *args, **kwargs):
        """Add the fields for the last mutation."""
        self.fields[self.ATTRIBUTE_MUTATION_METHOD] = Field(
            column_name=f"Mutation method", attribute=self.ATTRIBUTE_MUTATION_METHOD, readonly=True
        )
        self.fields[self.ATTRIBUTE_MUTATION_TRIGGER] = Field(
            column_name=f"Mutation trigger", attribute=self.ATTRIBUTE_MUTATION_TRIGGER, readonly=True
        )
        self.fields[self.ATTRIBUTE_MUTATION_SUCCESS] = Field(
            column_name=f"Mutation success", attribute=self.ATTRIBUTE_MUTATION_SUCCESS, readonly=True
        )
        self.fields[self.ATTRIBUTE_MUTATION_MESSAGE] = Field(
            column_name=f"Mutation message", attribute=self.ATTRIBUTE_MUTATION_MESSAGE, readonly=True
        )

    def export_mutation_field(self, field, obj):
        """Export the custom mutation fields."""
        latest_mutation = Mutation.objects.filter(object_id=obj.id, content_type=self.content_type).last()
        if latest_mutation is not None:
            if field.attribute == self.ATTRIBUTE_MUTATION_TRIGGER:
                return latest_mutation.trigger
            elif field.attribute == self.ATTRIBUTE_MUTATION_SUCCESS:
                return latest_mutation.success
            elif field.attribute == self.ATTRIBUTE_MUTATION_MESSAGE:
                return latest_mutation.message
            elif field.attribute == self.ATTRIBUTE_MUTATION_METHOD:
                return latest_mutation.method

        return None

    def export_field(self, field, obj):
        """Check for added mutation field before exporting."""
        if field.attribute in [
            self.ATTRIBUTE_MUTATION_TRIGGER,
            self.ATTRIBUTE_MUTATION_MESSAGE,
            self.ATTRIBUTE_MUTATION_SUCCESS,
            self.ATTRIBUTE_MUTATION_METHOD,
        ]:
            return self.export_mutation_field(field, obj)
        else:
            return super(CustomerResource, self).export_field(field, obj)

    class Meta:
        """Meta class."""

        model = models.Customer
        fields = [
            "uphance_id",
            "snelstart_id",
            "uphance_name",
            "snelstart_name",
        ]
        export_order = [
            "uphance_id",
            "snelstart_id",
            "uphance_name",
            "snelstart_name",
        ]
