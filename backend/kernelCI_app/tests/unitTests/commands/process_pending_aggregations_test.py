from django.test import SimpleTestCase

from kernelCI_app.management.commands.process_pending_aggregations import (
    _check_item_was_processed,
)
from kernelCI_app.models import ProcessedListingItems, SimplifiedStatusChoices

KEY = b"key"
CHECKOUT = "checkout-1"


def _entry(status=None, key=KEY, checkout_id=CHECKOUT):
    return ProcessedListingItems(
        listing_item_key=key, checkout_id=checkout_id, status=status
    )


def _check(*, existing=(), new_entries=(), item_status=SimplifiedStatusChoices.PASS):
    return _check_item_was_processed(
        existing_processed=set(existing),
        new_processed_entries=set(new_entries),
        listing_item_key=KEY,
        item_checkout_id=CHECKOUT,
        item_status=item_status,
    )


class CheckItemWasProcessedTest(SimpleTestCase):
    def test_unseen_item_is_counted_without_undo(self):
        self.assertEqual(_check(), (False, 0))

    def test_item_under_another_key_does_not_match(self):
        self.assertEqual(_check(existing=[_entry(key=b"other")]), (False, 0))

    def test_item_already_counted_with_a_status_is_skipped(self):
        self.assertEqual(
            _check(existing=[_entry(status=SimplifiedStatusChoices.FAIL)]), (True, 0)
        )

    def test_item_still_without_status_is_skipped(self):
        self.assertEqual(_check(existing=[_entry()], item_status=None), (True, 0))

    def test_item_that_gained_a_status_is_recounted_once(self):
        self.assertEqual(_check(existing=[_entry()]), (False, 1))

    def test_undo_is_doubled_when_both_passes_counted_it(self):
        """The committed entry and the in-batch entry each counted it as inconclusive."""
        new_entries = {_entry()}
        was_processed, decrements = _check_item_was_processed(
            existing_processed={_entry()},
            new_processed_entries=new_entries,
            listing_item_key=KEY,
            item_checkout_id=CHECKOUT,
            item_status=SimplifiedStatusChoices.PASS,
        )
        self.assertEqual((was_processed, decrements), (False, 2))
        self.assertEqual(new_entries, set())

    def test_no_undo_leaks_when_this_batch_already_recounted_it(self):
        """Guards a regression: the committed entry alone would ask for an undo, but this
        batch has already applied it, so the item must be a complete no-op."""
        self.assertEqual(
            _check(
                existing=[_entry()],
                new_entries=[_entry(status=SimplifiedStatusChoices.PASS)],
            ),
            (True, 0),
        )
