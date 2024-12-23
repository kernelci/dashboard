from typing import Literal

# "NULL" must be added manually because the database return None
type StatusValues = Literal["FAIL", "PASS", "SKIP", "ERROR", "MISS", "NULL"]
