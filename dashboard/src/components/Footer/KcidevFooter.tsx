import { memo, useMemo, useState, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { TbTerminal2 } from 'react-icons/tb';

import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import { serializeKcidevCommand, type KcidevCommand } from './kcidevCommand';

type CopyStatus = 'idle' | 'copied' | 'error';

const KcidevFooter = ({
  command,
}: {
  command?: KcidevCommand;
}): JSX.Element => {
  const [copyStatus, setCopyStatus] = useState<CopyStatus>('idle');
  const serializedCommand = useMemo(
    () => command && serializeKcidevCommand(command),
    [command],
  );

  const copyCommand = async (): Promise<void> => {
    if (!serializedCommand) {
      return;
    }

    setCopyStatus('idle');
    try {
      await navigator.clipboard.writeText(serializedCommand);
      setCopyStatus('copied');
    } catch {
      setCopyStatus('error');
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-center gap-2 text-center text-sm">
      <span>
        <FormattedMessage id="footer.description" />
      </span>
      {serializedCommand && command && (
        <Popover
          onOpenChange={open => {
            if (open) {
              setCopyStatus('idle');
            }
          }}
        >
          <PopoverTrigger asChild>
            <Button type="button" variant="outline">
              <TbTerminal2 aria-hidden="true" className="mr-2 size-5" />
              <FormattedMessage id="footer.cliCommand" />
            </Button>
          </PopoverTrigger>
          <PopoverContent
            className="w-[calc(100vw-2rem)] max-w-xl text-left"
            collisionPadding={16}
          >
            <h2 className="mb-3 text-base font-semibold">
              <FormattedMessage id="footer.commandTitle" />
            </h2>
            <pre
              aria-label={command.label}
              className="mb-3 max-w-full cursor-text overflow-x-auto rounded-md bg-slate-100 p-3 text-sm select-text"
              tabIndex={0}
            >
              <code>{serializedCommand}</code>
            </pre>
            {command.omittedFilters.length > 0 && (
              <div
                className="mb-3 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950"
                role="note"
              >
                <FormattedMessage
                  id="footer.unsupportedFilters"
                  values={{ filters: command.omittedFilters.join(', ') }}
                />
              </div>
            )}
            <div className="flex flex-wrap items-center gap-3">
              <Button type="button" onClick={copyCommand}>
                <FormattedMessage id="footer.copyCommand" />
              </Button>
              <a
                className="text-dark-blue underline"
                href="https://kci.dev"
                rel="noreferrer"
                target="_blank"
              >
                <FormattedMessage id="footer.installKcidev" />
              </a>
              <a
                className="text-dark-blue underline"
                href="https://kci.dev/results/"
                rel="noreferrer"
                target="_blank"
              >
                <FormattedMessage id="footer.commandDocumentation" />
              </a>
            </div>
            <div aria-live="polite" className="mt-3 min-h-5 text-sm">
              {copyStatus === 'copied' && (
                <FormattedMessage id="footer.copied" />
              )}
              {copyStatus === 'error' && (
                <span className="text-red" role="alert">
                  <FormattedMessage id="footer.copyError" />
                </span>
              )}
            </div>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
};

export const MemoizedKcidevFooter = memo(KcidevFooter);
