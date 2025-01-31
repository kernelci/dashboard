import { createFileRoute } from '@tanstack/react-router';

import IssueDetailsPage from '@/pages/IssueDetails/IssueDetails';

export const Route = createFileRoute('/issue/$issueId/')({
  component: IssueDetailsPage,
});
