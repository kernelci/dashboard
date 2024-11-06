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

const HardwareBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({
    from: '/hardware/$hardwareId/build/$buildId/',
  });
  const { buildId, hardwareId } = useParams({
    from: '/hardware/$hardwareId/build/$buildId/',
  });

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/build/$buildId',
  });

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
          <BreadcrumbLink to="/hardware" search={searchParams}>
            <FormattedMessage id="hardware.path" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbLink
          to="/hardware/$hardwareId"
          params={{ hardwareId }}
          search={searchParams}
        >
          <FormattedMessage id="hardware.details" />
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

export default HardwareBuildDetails;
