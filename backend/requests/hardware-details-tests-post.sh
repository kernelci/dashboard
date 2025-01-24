http POST http://localhost:8000/api/hardware/brcm,bcm2711/tests \
Content-Type:application/json \
<<< '{
    "origin":"maestro",
    "startTimestampInSeconds":1737487800,
    "endTimestampInSeconds":1737574200,
    "selectedCommits":{},
    "filter":{}
}'

# {
#    "tests":[
#       {
#          "id":"maestro:6790854709f33884b18d1be3",
#          "status":"SKIP",
#          "duration":null,
#          "path":"kselftest.dt.dt_test_unprobed_devices_sh_soc_avs-monitor_7d5d2000",
#          "start_time":"2025-01-22T05:42:31.798000Z",
#          "environment_compatible":[
#             "raspberrypi,4-model-b",
#             "brcm,bcm2711"
#          ],
#          "config":"defconfig",
#          "log_url":null,
#          "architecture":"arm64",
#          "compiler":"gcc-12",
#          "misc":{
#             "platform":"bcm2711-rpi-4-b"
#          }
#       },
#       {
#          "id":"maestro:6790854709f33884b18d1be2",
#          "status":"PASS",
#          "duration":null,
#          "path":"kselftest.dt.dt_test_unprobed_devices_sh_soc_avs-monitor_7d5d2000_thermal",
#          "start_time":"2025-01-22T05:42:31.798000Z",
#          "environment_compatible":[
#             "raspberrypi,4-model-b",
#             "brcm,bcm2711"
#          ],
#          "config":"defconfig",
#          "log_url":"https://kciapistagingstorage1.file.core.windows.net/production/kselftest-dt-6790844009f33884b18d145d/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#          "architecture":"arm64",
#          "compiler":"gcc-12",
#          "misc":{
#             "platform":"bcm2711-rpi-4-b"
#          }
#       },
#       ...
