# Database Logic

In this we translate the logic of the database fields and add details
that we should know


There are some resources that can be used as reference:
- [Grafana Dashboard](https://kcidb.kernelci.org/d/home/home?orgId=1&refresh=30m)
- [Submitter guide](https://docs.kernelci.org/kcidb/submitter_guide/)
- [kcidb json schema](https://github.com/kernelci/kcidb-io/blob/main/kcidb_io/schema/v04_03.py)

## Tree

A tree is a set of repos and branches, normally just one pair,
but more are possible. Essentially, a tree is a copy of the code base maintained
separately for a particular purpose.

Maestro maintains its own database of trees, where each is given a
name (`Checkouts.tree_name`), those names are generally
accepted and often recognized, but were chosen by
Maestro (KernelCI Legacy before it) developers and maintainers over a
period of time, and are not standardized, other CI systems are free
to report whatever they want there. Most choose not to report anything
in that field.

## Checkouts table

A checkout is a record of a CI system checking out a particular revision from
a particular git repository and branch. The json schema also says that checkouts
"represents the way the tested source code was obtained and its original
location. E.g. checking out a particular commit from a git repo, and applying
a set of patches on top."

## Test table

Tests are linked to a build

Important thing to look at the tests table is the `path` column, which is the
type of test that it is performing.They will be split in dots, which means that
is a child test from that test. `eg: boot.start` is a child of `boot`

- `start_time` is the time that a test has started, we can use that to graph
 X-Axis graphs of tests over time
 
- `status` Column show a status that can be `PASS` `SKIP` or `ERROR`

- `misc` - It is important to notice that the `misc` field can show the 
error message in case of an error

eg:
```json
{
  "arch": "arm64",
  "compiler": "gcc-12",
  "error_msg": "Invalid TESTCASE signal",
  "error_code": "Test",
  "kernel_type": "image"
}
```

- `environtment_misc` a JSON field that we can use for things about the environment
like detecting the platform, this is not set in stone and can change,
so we should double check the validation

```json
{
  "job_id": "14750408",
  "platform": "hp-x360-14a-cb0001xx-zork"
}
```

>NOTE: The contents of the `misc` field is not standardized, and shouldn't
>be relied upon to ever be used consistently by more than one
>CI system ("origin"), or even by the originating CI system itself, over time.
>The most it could be used for is a proof-of-concept.

In the tests table, the `environment_compatibles` column contains a 
sorted list of strings starting with the exact name of the machine, followed 
by an optional list of boards it is compatible with sorted from most compatible 
to least.

>NOTE: For more information about `environment_compatibles` these resources can 
be used as a reference:
> - [Platform Identification](https://docs.kernel.org/devicetree/usage-model.html#platform-identification)
> - [Compatible Description](https://github.com/kernelci/kcidb-io/blob/21ddf852d1de6740e8fdf3696d9ddd8b3fd53bcc/kcidb_io/schema/v04_05.py#L611)


## Revision

Revision has no respective table, but it is a collection of checkouts with
the same `git_commit_hash` and `patchset_hash`. But `patchset_hash` is not commmonly used these days.
