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

import { Skeleton } from '@/components/Skeleton';
import { useHardwareDetails } from '@/api/hardwareDetails';

import { HardwareHeader } from './HardwareDetailsHeaderTable';
import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';

function HardwareDetails(): JSX.Element {
  const searchParams = useSearch({ from: '/hardware/$hardwareId' });
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { intervalInDays } = useSearch({ from: '/hardware' });
  const { data, isLoading } = useHardwareDetails(hardwareId, intervalInDays);

  if (isLoading || !data)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return (
    <div className="flex flex-col pt-8">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink
              to="/hardware"
              search={previousParams => {
                return { ...previousParams, searchParams };
              }}
            >
              <FormattedMessage id="hardware.path" />
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>
              <span>{hardwareId}</span>
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <div className="mt-5">
        <HardwareHeader treeItems={data.trees} />
        <HardwareDetailsTabs
          HardwareDetailsData={data}
          hardwareId={hardwareId}
        />
      </div>
    </div>
  );
}

export default HardwareDetails;
