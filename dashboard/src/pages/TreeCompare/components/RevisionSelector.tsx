import type { JSX } from 'react';

import { ArrowLeftRight, GitBranch, History } from 'lucide-react';
import { FormattedMessage } from 'react-intl';

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

type RevisionSide = 'A' | 'B';

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

  return (
    <div
      className={cn(
        'flex flex-1 flex-col gap-3 rounded-lg border bg-white p-4',
        side === 'A' ? 'border-blue/40' : 'border-dim-gray/30',
      )}
    >
      <div className="flex items-center gap-2">
        <span
          className={cn(
            'inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold text-white',
            side === 'A' ? 'bg-blue' : 'bg-dim-gray',
          )}
        >
          {side}
        </span>
        <span className="text-dim-black text-sm font-semibold">
          <FormattedMessage
            id={side === 'A' ? 'treeCompare.sideA' : 'treeCompare.sideB'}
          />
        </span>
      </div>

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

      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={onPrevious}
          aria-label="Previous commit"
        >
          <History className="h-3.5 w-3.5" />
          <span className="sr-only">
            <FormattedMessage id="treeCompare.suggestion.previous" />
          </span>
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={onBranchHead}
          aria-label="Branch head"
        >
          <GitBranch className="h-3.5 w-3.5" />
          <span className="sr-only">
            <FormattedMessage id="treeCompare.suggestion.branchHead" />
          </span>
        </Button>
      </div>

      {selected && (
        <div className="text-dim-gray flex flex-col gap-1 text-sm">
          {selected.commitName && (
            <p className="text-dim-black truncate font-medium">
              {selected.commitName}
            </p>
          )}
          <TagChips tags={selected.tags} />
          <p className="text-xs">{selected.date}</p>
        </div>
      )}
    </div>
  );
}

interface RevisionSelectorBarProps {
  hashA: string;
  hashB: string;
  revisions: CompareRevision[];
  onHashAChange: (hash: string) => void;
  onHashBChange: (hash: string) => void;
  onSideAction: (side: RevisionSide, action: 'previous' | 'branchHead') => void;
  onSwap: () => void;
}

export function RevisionSelectorBar({
  hashA,
  hashB,
  revisions,
  onHashAChange,
  onHashBChange,
  onSideAction,
  onSwap,
}: RevisionSelectorBarProps): JSX.Element {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col items-stretch gap-4 lg:flex-row lg:items-center">
        <RevisionCard
          side="A"
          selectedHash={hashA}
          revisions={revisions}
          onSelect={onHashAChange}
          onPrevious={() => onSideAction('A', 'previous')}
          onBranchHead={() => onSideAction('A', 'branchHead')}
        />

        <div className="flex shrink-0 items-center justify-center">
          <button
            type="button"
            onClick={onSwap}
            className="bg-medium-gray flex h-10 w-10 items-center justify-center rounded-full"
            aria-label="Swap sides"
          >
            <ArrowLeftRight className="text-dim-gray h-5 w-5" />
            <span className="sr-only">
              <FormattedMessage id="treeCompare.suggestion.swap" />
            </span>
          </button>
        </div>

        <RevisionCard
          side="B"
          selectedHash={hashB}
          revisions={revisions}
          onSelect={onHashBChange}
          onPrevious={() => onSideAction('B', 'previous')}
          onBranchHead={() => onSideAction('B', 'branchHead')}
        />
      </div>
    </div>
  );
}
