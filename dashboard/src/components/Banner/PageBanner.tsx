import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';
import type { JSX } from 'react';
import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage, useIntl } from 'react-intl';

import { BaseBanner } from '@/components/Banner/BaseBanner';

const GITHUB_ISSUES_URL = 'https://github.com/kernelci/dashboard/issues';

interface IPageBanner {
  pageNameId: MessageDescriptor['id'];
  pageRoute: LinkProps['to'];
}

/**
 * This is the banner that goes in the older page
 */
export const OldPageBanner = ({
  pageNameId,
  pageRoute: newerPageRoute,
}: IPageBanner): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <BaseBanner>
      <FormattedMessage
        id="messages.olderPageVersion"
        values={{
          page: formatMessage({ id: pageNameId }),
          gitHubLink: (
            <a
              href={GITHUB_ISSUES_URL}
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              {formatMessage({ id: 'global.gitHubIssue' })}
            </a>
          ),
          newPageLink: (
            <Link to={newerPageRoute} className="underline">
              {formatMessage({ id: 'global.here' })}
            </Link>
          ),
        }}
      />
    </BaseBanner>
  );
};

/**
 * This is the banner that goes in the newer page
 */
export const NewPageBanner = ({
  pageNameId,
  pageRoute: olderPageRoute,
}: IPageBanner): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <BaseBanner variant="green">
      <FormattedMessage
        id="messages.newerPageVersion"
        values={{
          page: formatMessage({ id: pageNameId }),
          gitHubLink: (
            <a
              href={GITHUB_ISSUES_URL}
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              {formatMessage({ id: 'global.gitHubIssue' })}
            </a>
          ),
          oldVersionLink: (
            <Link to={olderPageRoute} className="underline">
              {formatMessage({ id: 'global.here' })}
            </Link>
          ),
        }}
      />
    </BaseBanner>
  );
};
