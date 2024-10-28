http 'http://localhost:8000/api/build/kernelci:kernelci.org:66a1d00e546da93e297e7073/tests'

# HTTP/1.1 200 OK
# Content-Length: 9122
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Wed, 31 Jul 2024 18:00:40 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.0
# Vary: origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
  #   {
  #     "id": "kernelci:kernelci.org:66a1d0d262f8cae67a7e7095",
  #     "duration": null,
  #     "status": "PASS",
  #     "path": "baseline.login",
  #     "startTime": "2024-07-25T04:13:06.105Z",
  #     "hardware": [
  #               "google,veyron-jaq-rev5",
  #               "google,veyron-jaq-rev4"
  #      ]
  #   },
  #   {
  #     "id": "kernelci:kernelci.org:66a1d0a38e8d1053a47e707c",
  #     "duration": null,
  #     "status": "PASS",
  #     "path": "baseline.login",
  #     "startTime": "2024-07-25T04:12:19.892Z",
  #      "hardware": [
  #                "google,veyron-jaq-rev5",
  #                "google,veyron-jaq-rev4"
  #            ]
  #   },
  #   {
  #     "id": "kernelci:kernelci.org:66a1d0a38e8d1053a47e707e",
  #     "duration": null,
  #     "status": "PASS",
  #     "path": "baseline.dmesg.emerg",
  #     "startTime": "2024-07-25T04:12:19.927Z",
  #     "hardware": [
  #               "google,veyron-jaq-rev5",
  #               "google,veyron-jaq-rev4"
  #      ]
  #   },
  #   ...
  # ]