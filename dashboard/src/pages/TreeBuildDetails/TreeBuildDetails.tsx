import { FormattedMessage } from 'react-intl';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

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
import type { TestsTableFilter } from '@/types/tree/TreeDetails';

const TreeBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/tree/$treeId/build/$buildId/' });
  const { buildId, treeId } = useParams({
    from: '/tree/$treeId/build/$buildId/',
  });

  const navigate = useNavigate({ from: '/tree/$treeId/build/$buildId' });

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              bootsTable: previousParams.tableFilter.bootsTable,
              buildsTable: previousParams.tableFilter.buildsTable,
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
      tableFilter={searchParams.tableFilter}
    />
  );
};

export default TreeBuildDetails;
