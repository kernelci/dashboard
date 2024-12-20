import { useParams } from '@tanstack/react-router';

import { IssueDetails } from '@/components/IssueDetails/IssueDetails';

const IssueDetailsPage = (): JSX.Element => {
  const { issueId, versionNumber } = useParams({
    from: '/issue/$issueId/version/$versionNumber',
  });

  return <IssueDetails issueId={issueId} versionNumber={versionNumber} />;
};

export default IssueDetailsPage;
