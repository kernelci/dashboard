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

const HardwareTestDetails = (): JSX.Element => {
  const searchParams = useSearch({
    from: '/hardware/$hardwareId/test/$testId/',
  });
  const { testId, hardwareId } = useParams({
    from: '/hardware/$hardwareId/test/$testId/',
  });

  return (
    <TestDetails
      testId={testId}
      context="hardware"
      breadcrumb={
        <Breadcrumb className="pb-6 pt-6">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink to="/hardware" search={searchParams}>
                <FormattedMessage id="hardware.path" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbLink
              to={`/hardware/$hardwareId`}
              params={{ hardwareId }}
              search={searchParams}
            >
              <FormattedMessage id="hardware.details" />
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

export default HardwareTestDetails;
