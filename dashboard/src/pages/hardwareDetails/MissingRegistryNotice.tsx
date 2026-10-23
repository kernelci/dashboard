import type { JSX } from 'react';
import { MdWarningAmber } from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
import CopyButton from '@/components/Button/CopyButton';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

type MissingRegistryNoticeProps = {
  platformId: string;
  compatibles: string[];
};

const MissingRegistryNotice = ({
  platformId,
  compatibles,
}: MissingRegistryNoticeProps): JSX.Element => {
  const compatibleList = compatibles.join(', ');

  return (
    <Collapsible
      className="group border-dark-gray mt-5 overflow-hidden rounded-xl border bg-white text-sm text-black"
      data-test-id="missing-registry-notice"
    >
      <CollapsibleTrigger asChild>
        <div className="flex w-full cursor-pointer items-center gap-2 bg-amber-50 px-3 py-2 text-left text-amber-950 dark:bg-amber-950 dark:text-amber-100">
          <MdWarningAmber className="size-5 shrink-0" aria-hidden />
          <span className="min-w-0 font-medium">
            <FormattedMessage
              id="hardwareDetails.missingRegistryTitle"
              values={{
                boardId: (
                  <span className="mx-0.5 inline-flex max-w-full items-center rounded bg-amber-200 px-1.5 py-0.5 align-baseline font-mono text-sm font-semibold text-amber-950 dark:bg-amber-800 dark:text-amber-50">
                    <span className="break-all">{platformId}</span>
                    <span
                      onClick={event => event.stopPropagation()}
                      onKeyDown={event => event.stopPropagation()}
                    >
                      <CopyButton value={platformId} />
                    </span>
                  </span>
                ),
              }}
            />
          </span>
          <ChevronRightAnimate className="ml-auto size-5 shrink-0" />
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <ul className="list-disc space-y-1 px-8 py-3">
          <li>
            <FormattedMessage
              id="hardwareDetails.missingRegistryItemFile"
              values={{
                registryLink: (
                  <a
                    href="https://github.com/kernelci/kernelci-pipeline/tree/main/config/hardware_registry"
                    target="_blank"
                    rel="noreferrer"
                    className="underline"
                  >
                    <FormattedMessage id="hardwareDetails.missingRegistryLink" />
                  </a>
                ),
              }}
            />
          </li>
          <li>
            <FormattedMessage id="hardwareDetails.missingRegistryItemFields" />
          </li>
          {compatibleList !== '' && (
            <li>
              <span className="inline-flex items-center">
                <FormattedMessage id="global.compatibles" />
                {': '}
                {compatibleList}
                <CopyButton value={compatibleList} />
              </span>
            </li>
          )}
        </ul>
      </CollapsibleContent>
    </Collapsible>
  );
};

export default MissingRegistryNotice;
