import { memo, useMemo, type JSX } from 'react';

import { useIntl } from 'react-intl';

import type { TIssueDetails } from '@/types/issueDetails';

import { OpenGraphTags } from './OpenGraphTags';

const IssueDetailsOGTags = ({
  title,
  issueCulprit,
  issueId,
  data,
}: {
  title: string;
  issueCulprit: string;
  issueId: string;
  data?: TIssueDetails;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const issueDetailsDescription: string = useMemo(() => {
    if (!data) {
      return formatMessage({ id: 'issueDetails.issueDetails' });
    }
    const versionDescription =
      formatMessage({ id: 'issueDetails.version' }) + ': ' + data?.version;

    const culpritDescription =
      formatMessage({ id: 'issueDetails.culpritTitle' }) + ': ' + issueCulprit;

    const firstSeen = data.extra?.[issueId]?.first_incident.first_seen;
    const firstSeenDescription = firstSeen
      ? formatMessage({ id: 'issue.firstSeen' }) +
        ': ' +
        new Date(firstSeen).toLocaleDateString()
      : '';

    const descriptionChunks = [
      versionDescription,
      culpritDescription,
      firstSeenDescription,
    ].filter(chunk => chunk !== '');

    return descriptionChunks.join(';\n');
  }, [data, formatMessage, issueCulprit, issueId]);

  return <OpenGraphTags title={title} description={issueDetailsDescription} />;
};

export const MemoizedIssueDetailsOGTags = memo(IssueDetailsOGTags);
