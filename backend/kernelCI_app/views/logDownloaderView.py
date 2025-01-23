from django.http import JsonResponse, HttpResponseBadRequest
from kernelCI_app.utils import getErrorResponseBody
from rest_framework.views import APIView
from bs4 import BeautifulSoup, Tag
import requests
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response


def scrape_log_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", id="list")
        if not table:
            return {"error": "Table with id 'list' not found"}

        tbody = table.find("tbody")
        if not isinstance(tbody, Tag):
            return {"error": "Table body not found"}

        log_data = []
        for row in tbody.find_all("tr"):
            if not isinstance(row, Tag):
                continue
            columns = row.find_all("td")
            if len(columns) == 3:
                file_name_cell = columns[0]
                file_name = file_name_cell.text.strip()
                if file_name.lower().startswith("parent directory"):
                    continue
                link = file_name_cell.find("a")
                url = link["href"]
                file_size = columns[1].text.strip()
                date = columns[2].text.strip()
                log_data.append(
                    {
                        "specific_log_url": url,
                        "file_name": file_name,
                        "file_size": file_size,
                        "date": date,
                    }
                )
            else:
                return {
                    "error": "Invalid number of columns in table row (probably not a log website)"
                }

        return {"log_files": log_data}
    except Exception as e:
        return {"error": str(e)}


class LogDownloaderView(APIView):
    def get(self, request):
        log_download_url = request.GET.get("log_download_url")
        parsed_data = scrape_log_data(log_download_url)

        error_message = parsed_data.get("error")
        if error_message:
            return HttpResponseBadRequest(getErrorResponseBody(error_message))

        if not parsed_data['log_files']:
            return create_error_response(
                error_message="No log files found", status_code=HTTPStatus.OK
            )

        return JsonResponse(parsed_data)
