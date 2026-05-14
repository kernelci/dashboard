import { useMemo, useState, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';
import { Check, ChevronsUpDown } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
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

type SelectorOption = {
  value: string;
  label: string;
};

const shortHash = (value: string): string => value.slice(0, SHORT_HASH_LENGTH);

interface HardwareRevisionSelectorsPresentationProps {
  treeOptions: SelectorOption[];
  branchOptions: SelectorOption[];
  revisionOptions: SelectorOption[];
  selectedTreeName?: string;
  selectedBranchValue?: string;
  selectedRevisionHash?: string;
  onTreeChange: (nextSelection: HardwareRevisionSelectorValue) => void;
}

interface HardwareRevisionComboboxProps {
  options: SelectorOption[];
  selectedValue?: string;
  onValueChange: (nextValue: string) => void;
  placeholder: string;
  searchPlaceholder: string;
  emptyMessage: string;
  dataTestId: string;
  disabled?: boolean;
}

const HardwareRevisionCombobox = ({
  options,
  selectedValue,
  onValueChange,
  placeholder,
  searchPlaceholder,
  emptyMessage,
  dataTestId,
  disabled = false,
}: HardwareRevisionComboboxProps): JSX.Element => {
  const [open, setOpen] = useState(false);
  const selectedOption = options.find(option => option.value === selectedValue);

  return (
    <Popover onOpenChange={setOpen} open={open}>
      <PopoverTrigger asChild>
        <Button
          aria-expanded={open}
          className={cn(
            'w-[220px] justify-between',
            !selectedOption && 'text-slate-500',
          )}
          data-test-id={dataTestId}
          disabled={disabled}
          role="combobox"
          variant="outline"
        >
          <span className="truncate">
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-[220px] p-0">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {options.map(option => (
                <CommandItem
                  key={option.value}
                  keywords={[option.label]}
                  onSelect={() => {
                    onValueChange(option.value);
                    setOpen(false);
                  }}
                  value={option.value}
                >
                  <span className="truncate">{option.label}</span>
                  <Check
                    className={cn(
                      'ml-auto h-4 w-4 shrink-0',
                      selectedValue === option.value
                        ? 'opacity-100'
                        : 'opacity-0',
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

const HardwareRevisionSelectorsPresentation = ({
  treeOptions,
  branchOptions,
  revisionOptions,
  selectedTreeName,
  selectedBranchValue,
  selectedRevisionHash,
  onTreeChange,
}: HardwareRevisionSelectorsPresentationProps): JSX.Element => {
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
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.treeSelectorLabel" />
        </span>
        <HardwareRevisionCombobox
          dataTestId="hardware-tree-selector"
          emptyMessage="No tree found."
          onValueChange={handleTreeChange}
          options={treeOptions}
          placeholder="Select tree"
          searchPlaceholder="Search tree..."
          selectedValue={selectedTreeName}
        />
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.branchSelectorLabel" />
        </span>
        <HardwareRevisionCombobox
          dataTestId="hardware-branch-selector"
          disabled={branchOptions.length === 0}
          emptyMessage="No branch found."
          onValueChange={handleBranchChange}
          options={branchOptions}
          placeholder="Select branch"
          searchPlaceholder="Search branch..."
          selectedValue={selectedBranchValue}
        />
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-dim-gray text-sm font-medium">
          <FormattedMessage id="hardwareListing.revisionSelectorLabel" />
        </span>
        <HardwareRevisionCombobox
          dataTestId="hardware-revision-selector"
          disabled={revisionOptions.length === 0}
          emptyMessage="No revision found."
          onValueChange={handleRevisionChange}
          options={revisionOptions}
          placeholder="Select revision"
          searchPlaceholder="Search revision..."
          selectedValue={selectedRevisionHash}
        />
      </div>
    </div>
  );
};

interface HardwareRevisionSelectorsProps {
  selectors: HardwareSelectorTree[];
  selectedTree: HardwareSelectorTree | null;
  selectedBranch: HardwareSelectorBranch | null;
  selection: HardwareRevisionSelection | null;
  onTreeChange: (nextSelection: HardwareRevisionSelectorValue) => void;
}

export const HardwareRevisionSelectors = ({
  selectors,
  selectedTree,
  selectedBranch,
  selection,
  onTreeChange,
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

  const selectedBranchValue = selection
    ? encodeBranchValue(selection.gitRepositoryUrl, selection.gitBranch)
    : undefined;

  return (
    <HardwareRevisionSelectorsPresentation
      treeOptions={treeOptions}
      branchOptions={branchOptions}
      revisionOptions={revisionOptions}
      selectedTreeName={selection?.treeName}
      selectedBranchValue={selectedBranchValue}
      selectedRevisionHash={selection?.gitCommitHash}
      onTreeChange={onTreeChange}
    />
  );
};
