import { useMemo, type JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';
import { IoClose } from 'react-icons/io5';

import { Button } from '@/components/ui/button';
import {
  Combobox,
  type ComboboxOption as SelectorOption,
} from '@/components/Combobox/Combobox';
import type {
  HardwareRevisionSelection,
  HardwareSelectorBranch,
  HardwareSelectorTree,
} from '@/types/hardware';

import {
  encodeBranchValue,
  type HardwareRevisionSelectorValue,
} from './hardwareSelection';

const SHORT_HASH_LENGTH = 12;

const shortHash = (value: string): string => value.slice(0, SHORT_HASH_LENGTH);

interface HardwareRevisionSelectorsPresentationProps {
  treeOptions: SelectorOption[];
  branchOptions: SelectorOption[];
  revisionOptions: SelectorOption[];
  selectedTreeName?: string;
  selectedBranchValue?: string;
  selectedRevisionHash?: string;
  onTreeChange: (nextSelection: HardwareRevisionSelectorValue) => void;
  onClearSelection: () => void;
}

const HardwareRevisionSelectorsPresentation = ({
  treeOptions,
  branchOptions,
  revisionOptions,
  selectedTreeName,
  selectedBranchValue,
  selectedRevisionHash,
  onTreeChange,
  onClearSelection,
}: HardwareRevisionSelectorsPresentationProps): JSX.Element => {
  const intl = useIntl();

  const treePlaceholder = intl.formatMessage({
    id: 'hardwareListing.treeSelectorPlaceholder',
  });
  const branchPlaceholder = intl.formatMessage({
    id: 'hardwareListing.branchSelectorPlaceholder',
  });
  const revisionPlaceholder = intl.formatMessage({
    id: 'hardwareListing.revisionSelectorPlaceholder',
  });

  const handleTreeChange = (nextTreeName: string): void => {
    onTreeChange({
      tree: nextTreeName,
      branch: '',
      revision: '',
    });
  };

  const handleBranchChange = (nextBranchValue: string): void => {
    onTreeChange({
      tree: selectedTreeName ?? '',
      branch: nextBranchValue,
      revision: '',
    });
  };

  const handleRevisionChange = (nextRevisionHash: string): void => {
    onTreeChange({
      tree: selectedTreeName ?? '',
      branch: selectedBranchValue ?? '',
      revision: nextRevisionHash,
    });
  };

  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.treeSelectorLabel" />
        </span>
        <Combobox
          dataTestId="hardware-tree-selector"
          emptyMessage={intl.formatMessage({
            id: 'hardwareListing.treeSelectorEmpty',
          })}
          onValueChange={handleTreeChange}
          options={treeOptions}
          placeholder={treePlaceholder}
          searchPlaceholder={intl.formatMessage({
            id: 'hardwareListing.treeSelectorSearchPlaceholder',
          })}
          selectedValue={selectedTreeName}
        />
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.branchSelectorLabel" />
        </span>
        <Combobox
          dataTestId="hardware-branch-selector"
          disabled={!selectedTreeName || branchOptions.length === 0}
          emptyMessage={intl.formatMessage({
            id: 'hardwareListing.branchSelectorEmpty',
          })}
          onValueChange={handleBranchChange}
          options={branchOptions}
          placeholder={branchPlaceholder}
          searchPlaceholder={intl.formatMessage({
            id: 'hardwareListing.branchSelectorSearchPlaceholder',
          })}
          selectedValue={selectedBranchValue}
        />
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.revisionSelectorLabel" />
        </span>
        <Combobox
          dataTestId="hardware-revision-selector"
          disabled={!selectedBranchValue || revisionOptions.length === 0}
          emptyMessage={intl.formatMessage({
            id: 'hardwareListing.revisionSelectorEmpty',
          })}
          onValueChange={handleRevisionChange}
          options={revisionOptions}
          placeholder={revisionPlaceholder}
          searchPlaceholder={intl.formatMessage({
            id: 'hardwareListing.revisionSelectorSearchPlaceholder',
          })}
          selectedValue={selectedRevisionHash}
        />
      </div>

      {selectedTreeName && (
        <Button
          aria-label={intl.formatMessage({
            id: 'hardwareListing.clearSelection',
          })}
          className="self-end"
          data-test-id="hardware-selection-clear"
          onClick={onClearSelection}
          size="icon"
          title={intl.formatMessage({ id: 'hardwareListing.clearSelection' })}
          variant="ghost"
        >
          <IoClose className="size-5" />
        </Button>
      )}
    </div>
  );
};

interface HardwareRevisionSelectorsProps {
  selectors: HardwareSelectorTree[];
  selectedTree: HardwareSelectorTree | null;
  selectedBranch: HardwareSelectorBranch | null;
  selection: HardwareRevisionSelection | null;
  onTreeChange: (nextSelection: HardwareRevisionSelectorValue) => void;
  onClearSelection: () => void;
}

export const HardwareRevisionSelectors = ({
  selectors,
  selectedTree,
  selectedBranch,
  selection,
  onTreeChange,
  onClearSelection,
}: HardwareRevisionSelectorsProps): JSX.Element => {
  const treeOptions: SelectorOption[] = selectors.map(tree => ({
    value: tree.tree_name,
    label: tree.tree_name,
  }));

  const branchOptions: SelectorOption[] = (selectedTree?.branches ?? []).map(
    branch => ({
      value: encodeBranchValue(
        branch.git_repository_url,
        branch.git_repository_branch,
      ),
      label: branch.git_repository_branch,
    }),
  );

  const revisionOptions: SelectorOption[] = useMemo(
    () =>
      (selectedBranch?.revisions ?? []).map(revision => ({
        value: revision.git_commit_hash,
        label: revision.git_commit_name ?? shortHash(revision.git_commit_hash),
      })),
    [selectedBranch?.revisions],
  );

  const selectedBranchValue = selectedBranch
    ? encodeBranchValue(
        selectedBranch.git_repository_url,
        selectedBranch.git_repository_branch,
      )
    : undefined;

  return (
    <HardwareRevisionSelectorsPresentation
      treeOptions={treeOptions}
      branchOptions={branchOptions}
      revisionOptions={revisionOptions}
      selectedTreeName={selectedTree?.tree_name}
      selectedBranchValue={selectedBranchValue}
      selectedRevisionHash={selection?.gitCommitHash}
      onTreeChange={onTreeChange}
      onClearSelection={onClearSelection}
    />
  );
};
