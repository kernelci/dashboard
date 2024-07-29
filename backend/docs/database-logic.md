# Database Logic

In this we translate the logic of the database fields and add details that we should know


## Tree
A tree has no respective table, but it is a collection of checkouts with the same `git_commit_hash` and `patchset_hash`, but pretty much nobody uses `patchset_hash` nowadays, so it will probably be `null` in most cases

> **Note:** There is an already in use Grafana dashboard that we can use to extract the logic
> Here is the link: https://kcidb.kernelci.org/d/home/home?orgId=1&refresh=30m


## Checkouts table
Checkouts consist when a CI check to a git branch and perform a build and its tests
A tree will have multiple checkouts, so they can have multiple builds


## Builds table
The builds that a checkout has performed.


## Test table

Tests are linked to a build

Important thing to look at the tests table is the `path` column, which is the type of test that it is performing.
They will be split in dots, which means that is a child test from that test. `eg: boot.start` is a child of `boot`

- `start_time` is the time that a test has started, we can use that to graph X-Axis graphs of tests over time
 
- `status` Column show a status that can be `PASS` `SKIP` or `ERROR` 

It is important to notice that the `misc` field will show the error message in case of an error

eg:
```
{
  "arch": "arm64",
  "compiler": "gcc-12",
  "error_msg": "Invalid TESTCASE signal",
  "error_code": "Test",
  "kernel_type": "image"
}
```

- `environtment_misc` is a field called environment misc which has a JSON and we can use for things about the environment like detecting the platform, this is not set in stone and can change,  so we should double check the validation

```
{
  "job_id": "14750408",
  "platform": "hp-x360-14a-cb0001xx-zork"
}
```