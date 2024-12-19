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
import { RedirectFrom } from '@/types/general';

const HardwareBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/build/$buildId' });
  const { buildId } = useParams({ from: '/build/$buildId' });
  const historyState = useRouterState({ select: s => s.location.state });
  const hardwareId = historyState.id;

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/build/$buildId',
  });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/hardware/$hardwareId/test/$testId',
      params: {
        testId: testId,
        hardwareId: hardwareId,
      },
      search: s => s,
    }),
    [hardwareId],
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
        state: { id: hardwareId, from: RedirectFrom.Hardware },
      });
    },
    [navigate, hardwareId],
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
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
      historyState={historyState}
    />
  );
};

export default HardwareBuildDetails;
