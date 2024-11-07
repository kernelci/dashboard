import { useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useHardwareDetails } from '@/api/hardwareDetails';

import { Skeleton } from '@/components/Skeleton';

import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';

function HardwareDetails(): JSX.Element {
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { intervalInDays } = useSearch({ from: '/hardware' });
  const { data, isLoading } = useHardwareDetails(hardwareId, intervalInDays);

  if (isLoading || !data)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return <HardwareDetailsTabs HardwareDetailsData={data} />;
}

export default HardwareDetails;
