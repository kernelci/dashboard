import { useIntl, FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
import { Separator } from '@/components/ui/separator';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import type {
  HardwareRegistrySyncFile,
  HardwareRegistrySyncResponse,
} from '@/types/hardware';
import { dateObjectToTimestampInSeconds, getFormattedDate } from '@/utils/date';

const FileLine = ({
  file,
}: {
  file: HardwareRegistrySyncFile;
}): JSX.Element => {
  const updatedAt = file.updated_at
    ? getFormattedDate(
        dateObjectToTimestampInSeconds(new Date(file.updated_at)),
      )
    : undefined;

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
      <a
        href={file.url}
        target="_blank"
        rel="noreferrer"
        className="font-medium underline"
      >
        {file.name}
      </a>
      {updatedAt ? (
        <span className="text-dark-gray2 text-xs">{updatedAt}</span>
      ) : null}
      <span className="text-dark-gray2 font-mono text-xs break-all">
        {file.content_hash}
      </span>
    </div>
  );
};

export const HardwareRegistrySync = ({
  sync,
}: {
  sync: HardwareRegistrySyncResponse;
}): JSX.Element => {
  const intl = useIntl();
  const [indexFile, ...otherFiles] = sync.files;

  return (
    <div className="text-sm">
      <Separator className="bg-dark-gray mb-4" />
      <div className="mb-2 flex flex-wrap items-baseline gap-x-3">
        <h2 className="text-base font-medium">
          <FormattedMessage id="hardwareListing.registryTitle" />
        </h2>
        <p className="text-dark-gray2 text-xs">
          <FormattedMessage id="hardwareListing.registrySyncDelay" />
        </p>
      </div>
      <Collapsible className="group">
        <div className="flex items-start gap-1">
          <CollapsibleTrigger
            className="mt-0.5 shrink-0"
            aria-label={intl.formatMessage({
              id: 'hardwareListing.registryFiles',
            })}
          >
            <ChevronRightAnimate />
          </CollapsibleTrigger>
          {indexFile ? <FileLine file={indexFile} /> : null}
        </div>
        <CollapsibleContent>
          <ul className="mt-2 flex flex-col gap-2 pl-7">
            {otherFiles.map(file => (
              <li key={file.url}>
                <FileLine file={file} />
              </li>
            ))}
          </ul>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
};
