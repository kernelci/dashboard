from django.http import JsonResponse
from rest_framework.views import APIView


class LogDownloaderView(APIView):
    def get(self, request):
        log_download_url = request.GET.get('log_download_url')
        print("LogDownloaderView")
        print("log_download_url: ", log_download_url)
        log_placeholders = [
                {
                    "file_name": "dmesg",
                    "file_size": 0,
                    "data": "11-11-11",
                    },
                ]
        return JsonResponse({"log_files": log_placeholders}) 
