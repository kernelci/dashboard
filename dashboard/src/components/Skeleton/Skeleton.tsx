import type { ReactNode } from 'react';

import { Skeleton as SkeletonComponent } from '@/components/ui/skeleton'; //to avoid name conflict we rename the import

type SkeletonProps = {
  children: ReactNode;
};

const Skeleton = ({ children }: SkeletonProps): JSX.Element => {
  return (
    <SkeletonComponent className="grid h-[400px] place-items-center">
      {children}
    </SkeletonComponent>
  );
};

export default Skeleton;
