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

const MILISECONDS_IN_ONE_SECOND = 1000;

const get_Timestamps = (
  intervalInDays: number,
): {
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
} => {
  const currentDate = new Date();
  currentDate.setDate(currentDate.getDate() - intervalInDays);
  const startTimestampInSeconds = Math.floor(
    currentDate.getTime() / MILISECONDS_IN_ONE_SECOND,
  );
  const endTimestampInSeconds = Math.floor(
    Date.now() / MILISECONDS_IN_ONE_SECOND,
  );

  return { startTimestampInSeconds, endTimestampInSeconds };
};

function HardwareDetails(): JSX.Element {
  const searchParams = useSearch({ from: '/hardware/$hardwareId' });
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { intervalInDays, origin } = useSearch({ from: '/hardware' });

  // TODO: actually we will get this from URL soon
  const { startTimestampInSeconds, endTimestampInSeconds } =
    get_Timestamps(intervalInDays);

  const { data, isLoading } = useHardwareDetails(
    hardwareId,
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
  );

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
