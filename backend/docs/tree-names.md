
# treeproof Command Documentation

The `treeproof` command generates and maintains a YAML file that maps KernelCI tree names to their git repository URLs. It uses the `Checkouts` database table as the source of truth and merges the results with any existing file to preserve previously known entries.

## Overview

This command:
- Reads existing tree-name mappings from the default trees file (if present)
- Scans `Checkouts` for unique `tree_name` and `git_repository_url` pairs
- Generates missing or duplicate tree names deterministically
- Gives priority to maestro-origin trees when conflicts occur
- Writes the merged result to the default trees file

It is possible to call the core of the command - `generate_tree_names()` - externally in the code as well. This will also update the file.

## Output

The command writes a YAML file with the following structure:

```
trees:
	tree_name:
		url: https://example.org/path/to/repo.git
```

If called in-code as `generate_tree_names()`, the function will return the formatted dict with the data that will/would be written into the tree-names file.

## Naming Rules

- If `tree_name` is missing, a name is derived from the git URL.
- If a `tree_name` already exists with a different URL, a numeric suffix is added (e.g., `linux-1`).
- Maestro-origin trees are processed first and take precedence over non-maestro trees.

## Examples

### Basic Usage

```
poetry run manage.py python3 treeproof
```

Result:

```yaml
trees:
  android:
    url: https://android.googlesource.com/kernel/common
  arm64:
    url: https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git
  axboe-linux:
    url: https://git.kernel.org/pub/scm/linux/kernel/git/axboe/linux.git
  ...
```

## Notes

- The output file location is determined by `BACKEND_VOLUME_DIR` and `TREE_NAMES_FILENAME`.
- The command always writes the file and returns the generated data to the caller.
