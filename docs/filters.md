# Filter logic

## How filters should work

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

## Adding a new filter

Our filter system is currently somewhat complex. Most of the parts are required, while some of them are unnecessary and should be addressed. For now, here are the steps for adding a new filter with our current structure. You don't necessarily need to do the backend steps first and then the frontend ones, mix and squash as sensible to a good commit split.

### In the backend

- Edit the summary and filter return fields of treeDetails/hardwareDetails, for both full and summary endpoints
- Add the filter logic to the FilterParams class
  - Add the relevant set, the handler function, update the "field: handler" map, and update the logic in the desired functions, such as `_is_build_filtered_out`
- Edit the tree/hardware commitHistory endpoint to be affected by the filter too
- Check unit tests to see if they need updates
- Check integration tests to see if they need updates
- Update backend schema with `generate_schema.sh` script

### In the frontend

- Edit the type that reflects the api response to include the new fields in summary and filters
- Add the card in the frontend
- Edit `zFilterObjectsKeys` or `zFilterNumberKeys` utils types to include the new filter. Edit the other related types to them as well, the components will flag the required types.
- Edit the mapFilterToReq function to translate the new filter to the backend format
- Edit the `TreeDetailsFilter`/`HardwareDetailsFilter` modal to include a new section and to transform the data into checkboxes
- Edit the search.ts file to map the filter name to a shortened version in the url
