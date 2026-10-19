import type { JSX } from 'react';
import { MdWarningAmber } from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

const MissingRegistryNotice = (): JSX.Element => {
  return (
    <Collapsible
      className="group border-dark-gray mt-5 overflow-hidden rounded-xl border bg-white text-sm text-black"
      data-test-id="missing-registry-notice"
    >
      <CollapsibleTrigger className="flex w-full items-center gap-2 bg-amber-50 px-3 py-2 text-left text-amber-950 dark:bg-amber-950 dark:text-amber-100">
        <MdWarningAmber className="size-5 shrink-0" aria-hidden />
        <span className="font-medium">
          <FormattedMessage id="hardwareDetails.missingRegistryTitle" />
        </span>
        <ChevronRightAnimate className="ml-auto size-5 shrink-0" />
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
        </ul>
      </CollapsibleContent>
    </Collapsible>
  );
};

export default MissingRegistryNotice;
