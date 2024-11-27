import { useParams, useRouterState, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import TestDetails from '@/components/TestDetails/TestDetails';

const TreeTestDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/test/$testId/' });
  const { testId } = useParams({ from: '/test/$testId/' });
  const treeId = useRouterState({ select: s => s.location.state.id });

  return (
    <TestDetails
      testId={testId}
      breadcrumb={
        <Breadcrumb className="pb-6 pt-6">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink to="/tree" search={searchParams}>
                <FormattedMessage id="tree.path" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbLink
              to={`/tree/$treeId`}
              params={{ treeId: treeId }}
              search={searchParams}
            >
              <FormattedMessage id="tree.details" />
            </BreadcrumbLink>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>
                <FormattedMessage id="test.details" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      }
    />
  );
};

export default TreeTestDetails;
