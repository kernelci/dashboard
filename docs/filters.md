# How filters should work

They should work as OR in the same category and AND between two different categories

Lets suppose we have a filter that is `"Boots Status" == 'MISS' or 'PASS'` 
and a filter `"Arch" == 'arm'` 

It means that:

| Status  |   Arch |  Should Show |
| ------- | ------ | ------------ |
| 'PASS'  | 'arm'  |    True      |
| 'PASS'  | 'x86'  |    False     |
| 'FAIL'  | 'arm'  |    False     |
| 'MISS'  | 'arm'  |    True      | 
| 'MISS'  | 'x86'  |    False     |
