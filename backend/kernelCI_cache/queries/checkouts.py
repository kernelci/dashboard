from kernelCI_cache.models import CheckoutsCache


def get_all_checkout_ids():
    checkouts = CheckoutsCache.objects.using("cache").values("checkout_id").all()
    return checkouts
