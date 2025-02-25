import { createFileRoute } from '@tanstack/react-router';

import IssueDetailsPage from '@/pages/IssueDetails/IssueDetails';

export const Route = createFileRoute('/_main/issue/$issueId/')({
  component: IssueDetailsPage,
});
