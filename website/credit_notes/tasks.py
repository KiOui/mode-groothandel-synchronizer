from django.conf import settings
from django.tasks import task
from credit_notes.models import CreditNote
from credit_notes.services import try_create_credit_note
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance


@task(queue_name="synchronize_credit_notes")
def synchronize_credit_notes():
    """Synchronize all credit notes."""
    first_credit_note = CreditNote.objects.all().order_by("uphance_id").first()
    if first_credit_note is not None:
        synchronize_credit_notes_from_id = first_credit_note.uphance_id
    else:
        synchronize_credit_notes_from_id = None

    # TODO: Make this configurable later.
    max_credit_notes_to_sync = 5

    uphance_client = Uphance.get_client()
    snelstart_client = Snelstart.get_client()

    if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
        raise SynchronizationError(f"Could not set the current Uphance organisation")

    credit_notes = uphance_client.credit_notes(since_id=synchronize_credit_notes_from_id)
    credit_notes = credit_notes.objects

    if max_credit_notes_to_sync is not None:
        credit_notes = credit_notes.objects[:max_credit_notes_to_sync]

    for credit_note in credit_notes:
        try_create_credit_note(uphance_client, snelstart_client, credit_note, Mutation.TRIGGER_CRON)
