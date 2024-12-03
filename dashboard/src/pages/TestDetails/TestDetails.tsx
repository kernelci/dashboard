import { useParams, useRouterState } from '@tanstack/react-router';

import TestDetails from '@/components/TestDetails/TestDetails';

import { RedirectFrom } from '@/types/general';

import TreeTestDetails from '@/pages/TreeTestDetails';
import HardwareTestDetails from '@/pages/HardwareTestDetails';

const TestDetailsPage = (): JSX.Element => {
  const historyState = useRouterState({ select: s => s.location.state });
  const { testId } = useParams({ from: '/test/$testId' });

  if (historyState.id !== undefined) {
    if (historyState.from === RedirectFrom.Tree) {
      return <TreeTestDetails />;
    }

    if (historyState.from === RedirectFrom.Hardware) {
      return <HardwareTestDetails />;
    }
  }

  return <TestDetails testId={testId} />;
};

export default TestDetailsPage;
