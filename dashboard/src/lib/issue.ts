import type { IntlFormatters } from 'react-intl';

import { valueOrEmpty } from '@/lib/string';
import type { TIssueDetails } from '@/types/issueDetails';

export const getIssueCulprit = ({
  culprit_code,
  culprit_harness,
  culprit_tool,
  formatMessage,
}: {
  culprit_code: TIssueDetails['culprit_code'];
  culprit_harness: TIssueDetails['culprit_harness'];
  culprit_tool: TIssueDetails['culprit_tool'];
  formatMessage: IntlFormatters['formatMessage'];
}): string => {
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

  return valueOrEmpty(result.join(', '));
};
