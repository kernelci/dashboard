import { useParams, useSearch } from '@tanstack/react-router';

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
  const searchParams = useSearch({ from: '/tree/$treeId/test/$testId/' });
  const { testId, treeId } = useParams({ from: '/tree/$treeId/test/$testId/' });

  return (
    <TestDetails
      testId={testId}
      context="tree"
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
