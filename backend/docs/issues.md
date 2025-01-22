# Issues

Issues are objects that group several results, they can be related to tests and/or builds, being related in the database through the `incidents` table.

Issues are usually registered for failed results, but keep in mind that they can also appear for inconclusive results (anything that is not PASS or FAIL for tests).
