import type { JSX } from 'react';

import { ArrowLeftRight, GitBranch, History } from 'lucide-react';
import { FormattedMessage } from 'react-intl';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import type { CompareRevision } from '@/types/tree/TreeCompare';

import { cn } from '@/lib/utils';

export type RevisionSide = 'base' | 'compare';

function TagChips({ tags }: { tags: string[] }): JSX.Element | null {
  if (tags.length === 0) {
    return null;
  }

  return (
    <span className="inline-flex flex-wrap gap-1">
      {tags.map(tag => (
        <span
          key={tag}
          className="bg-medium-light-blue text-dark-blue inline-flex items-center rounded-full px-2 py-0.5 font-mono text-xs font-semibold"
        >
          {tag}
        </span>
      ))}
    </span>
  );
}

export function targetRevision(
  revisions: CompareRevision[],
  selectedHash: string,
  action: 'previous' | 'branchHead',
): CompareRevision | undefined {
  if (action === 'branchHead') {
    return revisions[0];
  }
  const currentIndex = revisions.findIndex(
    revision => revision.hash === selectedHash,
  );
  const previousIndex = Math.min(
    revisions.length - 1,
    Math.max(currentIndex, 0) + 1,
  );
  return revisions[previousIndex];
}

function RevisionDetails({
  revision,
}: {
  revision: CompareRevision;
}): JSX.Element {
  return (
    <div className="flex flex-col gap-1 text-sm">
      <span className="font-mono text-xs">{revision.shortHash}</span>
      {revision.commitName && (
        <span className="text-dim-black font-medium">
          {revision.commitName}
        </span>
      )}
      <TagChips tags={revision.tags} />
      {revision.date && (
        <span className="text-dim-gray text-xs">{revision.date}</span>
      )}
    </div>
  );
}

function RevisionCard({
  side,
  selectedHash,
  revisions,
  onSelect,
  onPrevious,
  onBranchHead,
}: {
  side: RevisionSide;
  selectedHash: string;
  revisions: CompareRevision[];
  onSelect: (hash: string) => void;
  onPrevious: () => void;
  onBranchHead: () => void;
}): JSX.Element {
  const selected = revisions.find(r => r.hash === selectedHash);
  const previousRevision = targetRevision(revisions, selectedHash, 'previous');
  const branchHeadRevision = targetRevision(
    revisions,
    selectedHash,
    'branchHead',
  );

  return (
    <div
      className={cn(
        'flex flex-1 flex-col gap-3 rounded-lg border bg-white p-4',
        side === 'base' ? 'border-blue/40' : 'border-dim-gray/30',
      )}
    >
      <span className="text-dim-black text-sm font-semibold">
        <FormattedMessage
          id={side === 'base' ? 'treeCompare.base' : 'treeCompare.compare'}
        />
      </span>

      <Select value={selectedHash} onValueChange={onSelect}>
        <SelectTrigger className="w-full">
          <SelectValue
            placeholder={<FormattedMessage id="treeCompare.selectRevision" />}
          />
        </SelectTrigger>
        <SelectContent>
          {revisions.map(revision => (
            <SelectItem key={revision.hash} value={revision.hash}>
              <span className="inline-flex max-w-full items-center gap-2">
                <span className="font-mono text-sm">{revision.shortHash}</span>
                <TagChips tags={revision.tags} />
                {revision.commitName && (
                  <span className="text-dim-gray border-l border-gray-300 pl-2 text-sm">
                    {revision.commitName}
                  </span>
                )}
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="flex flex-wrap items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={onPrevious}
            >
              <History className="h-3.5 w-3.5" />
              <FormattedMessage id="treeCompare.suggestion.previous" />
            </Button>
          </TooltipTrigger>
          {previousRevision && (
            <TooltipContent className="max-w-xs">
              <RevisionDetails revision={previousRevision} />
            </TooltipContent>
          )}
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={onBranchHead}
            >
              <GitBranch className="h-3.5 w-3.5" />
              <FormattedMessage id="treeCompare.suggestion.branchHead" />
            </Button>
          </TooltipTrigger>
          {branchHeadRevision && (
            <TooltipContent className="max-w-xs">
              <RevisionDetails revision={branchHeadRevision} />
            </TooltipContent>
          )}
        </Tooltip>
      </div>

      {selected && <RevisionDetails revision={selected} />}
    </div>
  );
}

interface RevisionSelectorBarProps {
  baseHash: string;
  compareHash: string;
  revisions: CompareRevision[];
  onBaseChange: (hash: string) => void;
  onCompareChange: (hash: string) => void;
  onSideAction: (side: RevisionSide, action: 'previous' | 'branchHead') => void;
  onSwap: () => void;
}

export function RevisionSelectorBar({
  baseHash,
  compareHash,
  revisions,
  onBaseChange,
  onCompareChange,
  onSideAction,
  onSwap,
}: RevisionSelectorBarProps): JSX.Element {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col items-stretch gap-4 lg:flex-row lg:items-center">
        <RevisionCard
          side="base"
          selectedHash={baseHash}
          revisions={revisions}
          onSelect={onBaseChange}
          onPrevious={() => onSideAction('base', 'previous')}
          onBranchHead={() => onSideAction('base', 'branchHead')}
        />

        <div className="flex shrink-0 items-center justify-center">
          <button
            type="button"
            onClick={onSwap}
            className="bg-medium-gray flex h-10 w-10 items-center justify-center rounded-full"
            aria-label="Swap base and compare"
          >
            <ArrowLeftRight className="text-dim-gray h-5 w-5" />
            <span className="sr-only">
              <FormattedMessage id="treeCompare.suggestion.swap" />
            </span>
          </button>
        </div>

        <RevisionCard
          side="compare"
          selectedHash={compareHash}
          revisions={revisions}
          onSelect={onCompareChange}
          onPrevious={() => onSideAction('compare', 'previous')}
          onBranchHead={() => onSideAction('compare', 'branchHead')}
        />
      </div>
    </div>
  );
}
