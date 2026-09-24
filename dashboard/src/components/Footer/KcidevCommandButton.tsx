import { memo, useMemo, useState, type JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { TbCopy, TbTerminal2 } from 'react-icons/tb';

import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import {
  serializeShellArgv,
  type KcidevCommand,
  type KcidevCommandVariant,
} from './kcidevCommand';

type CopyStatus = 'idle' | 'copied' | 'error';

const KcidevCommandButton = ({
  command,
}: {
  command?: KcidevCommand | readonly KcidevCommand[];
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const [copyStatus, setCopyStatus] = useState<CopyStatus>('idle');
  const [selectedVariants, setSelectedVariants] = useState<
    Record<string, KcidevCommandVariant['id']>
  >({});
  const commands = useMemo<readonly KcidevCommand[]>(
    () =>
      command
        ? Array.isArray(command)
          ? command
          : [command as KcidevCommand]
        : [],
    [command],
  );

  const copyCommand = async (argv: readonly string[]): Promise<void> => {
    setCopyStatus('idle');
    try {
      await navigator.clipboard.writeText(serializeShellArgv(argv));
      setCopyStatus('copied');
    } catch {
      setCopyStatus('error');
    }
  };

  if (commands.length === 0) {
    return <></>;
  }

  return (
    <div className="shrink-0 text-sm">
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
          {commands.map(value => {
            const variants = value.variants;
            const selectedId = selectedVariants[value.id] ?? 'human';
            const variant =
              variants.find(candidate => candidate.id === selectedId) ??
              variants[0];
            const commandLabel = `${value.label}: ${variant.label}`;

            return (
              <section className="mb-4" key={value.id}>
                <h3 className="mb-1 text-sm font-medium">{value.label}</h3>
                {variants.length > 1 && (
                  <Select
                    value={variant.id}
                    onValueChange={id => {
                      setSelectedVariants(previous => ({
                        ...previous,
                        [value.id]: id as KcidevCommandVariant['id'],
                      }));
                      setCopyStatus('idle');
                    }}
                  >
                    <SelectTrigger
                      aria-label={`${value.label} output format`}
                      className="mb-2 h-8"
                    >
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {variants.map(candidate => (
                        <SelectItem key={candidate.id} value={candidate.id}>
                          {candidate.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
                <div className="flex items-start gap-2">
                  <pre
                    aria-label={commandLabel}
                    className="min-w-0 flex-1 cursor-text overflow-x-auto rounded-md bg-slate-100 p-3 text-sm select-text"
                    tabIndex={0}
                  >
                    <code>{serializeShellArgv(variant.argv)}</code>
                  </pre>
                  <Button
                    aria-label={`${formatMessage({ id: 'footer.copyCommand' })}: ${variant.label}`}
                    className="size-9 shrink-0 p-0"
                    type="button"
                    onClick={() => copyCommand(variant.argv)}
                  >
                    <TbCopy aria-hidden="true" className="size-5" />
                  </Button>
                </div>
                {variant.writesFiles && (
                  <p className="mt-2 text-sm font-medium">
                    <FormattedMessage id="footer.writesFiles" />
                  </p>
                )}
                {value.omittedFilters.length > 0 && (
                  <div
                    className="mt-2 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950"
                    role="note"
                  >
                    <FormattedMessage
                      id="footer.unsupportedFilters"
                      values={{ filters: value.omittedFilters.join(', ') }}
                    />
                  </div>
                )}
              </section>
            );
          })}
          <a
            className="text-dark-blue underline"
            href="https://kci.dev/results/"
            rel="noreferrer"
            target="_blank"
          >
            <FormattedMessage id="footer.commandDocumentation" />
          </a>
          <div aria-live="polite" className="mt-3 min-h-5 text-sm">
            {copyStatus === 'copied' && <FormattedMessage id="footer.copied" />}
            {copyStatus === 'error' && (
              <span className="text-red" role="alert">
                <FormattedMessage id="footer.copyError" />
              </span>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};

export const MemoizedKcidevCommandButton = memo(KcidevCommandButton);
