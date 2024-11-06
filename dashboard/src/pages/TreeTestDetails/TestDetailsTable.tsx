import { ErrorBoundary } from 'react-error-boundary';

import type { TTestDetails } from '@/types/tree/TestDetails';

type TTestDetailsTableProps = {
  tests: TTestDetails[];
};

const TestDetailsTable = ({ tests }: TTestDetailsTableProps): JSX.Element => {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <div className="overflow-x-auto">
        {tests.map(test => (
          <div key={test.id}>
            <pre>{JSON.stringify(test, null, 2)}</pre>
          </div>
        ))}
      </div>
    </ErrorBoundary>
  );
};

export default TestDetailsTable;
