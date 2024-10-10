from django.http import JsonResponse
from rest_framework.views import APIView
from bs4 import BeautifulSoup
import requests

def scrape_log_data(url):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the table with the file data
    table = soup.find('table', id='list')

    # Extract the data from each row of the table
    log_data = []
    for row in table.find('tbody').find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 3:
            file_name = columns[0].text.strip()
            file_size = columns[1].text.strip()
            date = columns[2].text.strip()
            log_data.append({
                'file_name': file_name,
                'file_size': file_size,
                'date': date
            })

    return log_data
class LogDownloaderView(APIView):
    def get(self, request):
        log_download_url = request.GET.get('log_download_url')
        print("LogDownloaderView")
        print("log_download_url: ", log_download_url)
        parsed_data = scrape_log_data(log_download_url)

        print("parsed_data: ", parsed_data)

        log_placeholders = [
                {
                    "file_name": "dmesg",
                    "file_size": 0,
                    "data": "11-11-11",
                    },
                ]
        return JsonResponse({"log_files": log_placeholders}) 
