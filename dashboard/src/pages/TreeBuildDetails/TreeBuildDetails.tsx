import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { useCallback } from 'react';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import BuildDetails from '@/components/BuildDetails/BuildDetails';
import {
  zTableFilterInfoDefault,
  type TestsTableFilter,
} from '@/types/tree/TreeDetails';

const TreeBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/build/$buildId' });
  const { buildId } = useParams({ from: '/build/$buildId' });
  const treeId = useRouterState({ select: s => s.location.state.id });

  const navigate = useNavigate({ from: '/tree/$treeId/build/$buildId' });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: testId,
        treeId: treeId,
      },
      search: s => s,
    }),
    [treeId],
  );

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
            },
          };
        },
      });
    },
    [navigate],
  );

  const breadcrumbElement = (
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
            <FormattedMessage id="buildDetails.buildDetails" />
          </BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );

  return (
    <BuildDetails
      buildId={buildId}
      breadcrumb={breadcrumbElement}
      onClickFilter={onClickFilter}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default TreeBuildDetails;
