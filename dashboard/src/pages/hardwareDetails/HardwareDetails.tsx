import { useParams } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useHardwareDetails } from '@/api/hardwareDetails';

import { Skeleton } from '@/components/Skeleton';

import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';

const DEFAULT_DAYS_INTERVAL = 1;

function HardwareDetails(): JSX.Element {
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { data, isLoading } = useHardwareDetails(
    hardwareId,
    DEFAULT_DAYS_INTERVAL,
  );

  if (isLoading || !data)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return <HardwareDetailsTabs HardwareDetailsData={data} />;
}

export default HardwareDetails;
