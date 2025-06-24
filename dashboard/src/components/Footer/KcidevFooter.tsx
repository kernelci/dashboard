import { memo, useMemo, type JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { TbTerminal2 } from 'react-icons/tb';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

// These types define the possible args of the command,
// including their variation (command after `kci-dev results`)
type TreeDetailsCmdFlags = {
  cmdName: 'summary' | 'builds' | 'boots' | 'tests';
  'git-url'?: string;
  branch?: string;
  commit: string;
};

type DetailsCmdFlags = {
  cmdName: 'build' | 'boot' | 'test';
  id: string;
  'download-logs': boolean;
  json: boolean;
};

type HardwareDetailsCmdFlags = {
  cmdName:
    | 'hardware summary'
    | 'hardware builds'
    | 'hardware boots'
    | 'hardware tests';
  name: string;
  origin: string;
  json?: boolean;
};

type HardwareListingCmdFlags = {
  cmdName: 'hardware list';
  origin: string;
  json: boolean;
};

type TreeListingCmdFlags = {
  cmdName: 'trees';
};

// This map dictates which flags each commandGroup will accept
type CommandArgsMap = {
  treeDetails: TreeDetailsCmdFlags;
  details: DetailsCmdFlags;
  hardwareDetails: HardwareDetailsCmdFlags;
  hardwareListing: HardwareListingCmdFlags;
  trees: TreeListingCmdFlags;
  issue: never;
};

// This type and map will tell which arguments will be added as `command value` or `command --key value`
type PositionalArgs = {
  required: string[];
  flags: string[];
};

const commandArgs: {
  [K in keyof CommandArgsMap]: PositionalArgs;
} = {
  treeDetails: {
    required: ['cmdName'],
    flags: ['git-url', 'branch', 'commit'],
  },
  details: {
    required: ['cmdName'],
    flags: ['id', 'download-logs', 'json'],
  },
  hardwareDetails: {
    required: ['cmdName'],
    flags: ['name', 'origin', 'json'],
  },
  hardwareListing: {
    required: ['cmdName'],
    flags: ['origin', 'json'],
  },
  trees: {
    required: ['cmdName'],
    flags: [],
  },
  issue: {
    required: [],
    flags: [],
  },
};

const BASECOMMAND = 'kci-dev results';

const buildCommand = <K extends keyof CommandArgsMap>(
  commandGroup: K,
  args: CommandArgsMap[K],
): string | undefined => {
  const parts = [BASECOMMAND];

  for (const key in args) {
    if (Object.prototype.hasOwnProperty.call(args, key)) {
      const value = args[key];
      if (value) {
        if (commandArgs[commandGroup]['required'].includes(key)) {
          parts.push(String(value));
        } else {
          if (typeof value === 'boolean' && value) {
            parts.push(`--${key}`);
          } else {
            parts.push(`--${key} '${value}'`);
          }
        }
      } else {
        // for the purpose of the examples, if some of the values
        // are missing then we don't return the command
        return undefined;
      }
    }
  }

  return parts.join(' ');
};

// TODO: there are better ways of passing the args,
// one of them could be changing the parameters of the component itself
// instead of passing the args inside an object, which would also help with memoization
const KcidevFooter = <K extends keyof CommandArgsMap>({
  commandGroup,
  args,
}: {
  commandGroup: K;
  args?: CommandArgsMap[K];
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

  const command = useMemo(() => {
    if (!args) {
      return;
    }

    return buildCommand(commandGroup, args);
  }, [commandGroup, args]);

  return (
    <div className="flex justify-center text-center align-middle text-[14px]">
      <span className="inline">
        <span className="mr-1 font-bold">
          <FormattedMessage id="footer.question" />
        </span>
        <FormattedMessage id="footer.kcidev" values={{ link: kcidevLink }} />
      </span>
      {command && (
        <TooltipIcon
          tooltipId="footer.command"
          tooltipValues={{ command: command }}
          icon={<TbTerminal2 className="ml-2 size-5" />}
        />
      )}
    </div>
  );
};

export const MemoizedKcidevFooter = memo(KcidevFooter);
