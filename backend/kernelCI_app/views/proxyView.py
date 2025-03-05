import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema


class ProxyView(APIView):
    """
    Proxy view for fetching log files and handling CORS issues.
    """
    
    @extend_schema(
        description="Proxy endpoint to fetch log files from external sources",
        responses={200: bytes},  # Raw binary response
    )
    def get(self, request):
        url = request.GET.get('url')
        if not url:
            return Response({"error": "URL parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Forward the request to the target URL
            response = requests.get(url, stream=True)
            
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch resource: {response.reason}"},
                    status=response.status_code
                )
            
            # Create a Django response with the same content type
            
            proxy_response = HttpResponse(
                content=response.content,
                content_type=response.headers.get('Content-Type', 'application/octet-stream')
            )

            
            # Add Content-Disposition if present
            if 'Content-Disposition' in response.headers:
                proxy_response['Content-Disposition'] = response.headers['Content-Disposition']
            
            # Add Content-Length if present
            if 'Content-Length' in response.headers:
                proxy_response['Content-Length'] = response.headers['Content-Length']
                
            return proxy_response
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Error fetching the resource: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
