import { memo, useMemo, type JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { TbTerminal2 } from 'react-icons/tb';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

import { serializeKcidevCommand, type KcidevCommand } from './kcidevCommand';

const KcidevFooter = ({
  command,
}: {
  command?: KcidevCommand;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const kcidevLink = useMemo(() => {
    return (
      <a
        href="https://kci.dev"
        target="_blank"
        rel="noreferrer"
        className="text-dark-blue underline"
      >
        {formatMessage({ id: 'global.kcidev' })}
      </a>
    );
  }, [formatMessage]);

  const serializedCommand = useMemo(
    () => command && serializeKcidevCommand(command),
    [command],
  );

  return (
    <div className="flex justify-center text-center align-middle text-[14px]">
      <span className="inline">
        <span className="mr-1 font-bold">
          <FormattedMessage id="footer.question" />
        </span>
        <FormattedMessage id="footer.kcidev" values={{ link: kcidevLink }} />
      </span>
      {serializedCommand && (
        <TooltipIcon
          tooltipId="footer.command"
          tooltipValues={{ command: serializedCommand }}
          icon={<TbTerminal2 className="ml-2 size-5" />}
        />
      )}
    </div>
  );
};

export const MemoizedKcidevFooter = memo(KcidevFooter);
