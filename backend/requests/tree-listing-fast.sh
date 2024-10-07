# If you want to see headers, add -p H to the http call:
# http -p H 'http://localhost:8000/api/tree/' origin==maestro
http 'http://localhost:8000/api/tree-fast/' origin==maestro

# If you want to provide another limit to query:
# http 'http://localhost:8000/api/tree-fast/' origin==maestro intervalInDays==8