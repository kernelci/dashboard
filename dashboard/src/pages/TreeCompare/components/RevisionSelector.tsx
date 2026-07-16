import type { JSX } from 'react';

import { ArrowLeftRight } from 'lucide-react';
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

function RevisionCard({
  side,
  selectedHash,
  revisions,
  onSelect,
}: {
  side: RevisionSide;
  selectedHash: string;
  revisions: CompareRevision[];
  onSelect: (hash: string) => void;
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
              <span className="font-mono text-sm">{revision.shortHash}</span>
              {revision.commitName && (
                <span className="text-dim-gray ml-2">
                  — {revision.commitName}
                </span>
              )}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {selected && (
        <div className="text-dim-gray text-sm">
          {selected.commitName && (
            <p className="text-dim-black truncate font-medium">
              {selected.commitName}
            </p>
          )}
          <p className="font-mono text-xs">{selected.shortHash}</p>
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
  onSuggestion: (suggestion: 'previous' | 'branchHead' | 'swap') => void;
}

export function RevisionSelectorBar({
  hashA,
  hashB,
  revisions,
  onHashAChange,
  onHashBChange,
  onSuggestion,
}: RevisionSelectorBarProps): JSX.Element {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col items-stretch gap-4 lg:flex-row lg:items-center">
        <RevisionCard
          side="A"
          selectedHash={hashA}
          revisions={revisions}
          onSelect={onHashAChange}
        />

        <div className="flex shrink-0 items-center justify-center">
          <div className="bg-medium-gray flex h-10 w-10 items-center justify-center rounded-full">
            <ArrowLeftRight className="text-dim-gray h-5 w-5" />
          </div>
        </div>

        <RevisionCard
          side="B"
          selectedHash={hashB}
          revisions={revisions}
          onSelect={onHashBChange}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-dim-gray text-sm">
          <FormattedMessage id="treeCompare.suggestions" />:
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSuggestion('previous')}
        >
          <FormattedMessage id="treeCompare.suggestion.previous" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSuggestion('branchHead')}
        >
          <FormattedMessage id="treeCompare.suggestion.branchHead" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSuggestion('swap')}
        >
          <FormattedMessage id="treeCompare.suggestion.swap" />
        </Button>
      </div>
    </div>
  );
}
