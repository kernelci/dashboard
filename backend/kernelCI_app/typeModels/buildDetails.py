from kernelCI_app.typeModels.commonDetails import BuildHistoryItem
from kernelCI_app.typeModels.databases import (
    Origin,
    Timestamp,
    Checkout__Id,
    Checkout__TreeName,
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
    Build__Command,
    Build__Comment,
    Build__LogExcerpt,
    Build__InputFiles,
    Build__OutputFiles,
)


class BuildDetailsResponse(BuildHistoryItem):
    _timestamp: Timestamp
    checkout_id: Checkout__Id
    command: Build__Command
    comment: Build__Comment
    tree_name: Checkout__TreeName
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    git_commit_tags: Checkout__GitCommitTags
    origin: Origin
    log_excerpt: Build__LogExcerpt
    input_files: Build__InputFiles
    output_files: Build__OutputFiles
