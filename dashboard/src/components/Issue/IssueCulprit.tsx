import { useIntl } from 'react-intl';

import { useMemo, type JSX } from 'react';

import type { TIssueDetails } from '@/types/issueDetails';
import { valueOrEmpty } from '@/lib/string';

interface IIssueCulprit {
  culprit_code: TIssueDetails['culprit_code'];
  culprit_harness: TIssueDetails['culprit_harness'];
  culprit_tool: TIssueDetails['culprit_tool'];
}

export const IssueCulprit = ({
  culprit_code,
  culprit_harness,
  culprit_tool,
}: IIssueCulprit): JSX.Element => {
  const { formatMessage } = useIntl();

  const culprits: string[] = useMemo(() => {
    const result: string[] = [];
    if (culprit_code) {
      result.push(formatMessage({ id: 'issueDetails.culpritCode' }));
    }
    if (culprit_harness) {
      result.push(formatMessage({ id: 'issueDetails.culpritHarness' }));
    }
    if (culprit_tool) {
      result.push(formatMessage({ id: 'issueDetails.culpritTool' }));
    }

    return result;
  }, [culprit_code, culprit_harness, culprit_tool, formatMessage]);

  return <span>{valueOrEmpty(culprits.join(', '))}</span>;
};
