import { ReactElement } from 'react';

import { useFeatureFlag } from '@/hooks/useFeatureFlag';

export const DevOnly = ({
  children,
}: {
  children: ReactElement;
}): JSX.Element => {
  const { showDev } = useFeatureFlag();

  return <>{showDev ? children : null}</>;
};
