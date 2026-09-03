from django.http import JsonResponse


def health(_request) -> JsonResponse:
    return JsonResponse({"status": "ok"})
