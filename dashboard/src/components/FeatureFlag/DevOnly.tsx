import { ReactNode } from 'react';

import { useFeatureFlag } from '@/hooks/useFeatureFlag';

export const DevOnly = ({ children }: { children: ReactNode }): JSX.Element => {
  const { showDev } = useFeatureFlag();

  return <>{showDev ? children : null}</>;
};
