import type { ReactNode, ComponentProps } from 'react';

import { Skeleton as SkeletonComponent } from '@/components/ui/skeleton'; //to avoid name conflict we rename the import

import { cn } from '@/lib/utils';

type SkeletonProps = ComponentProps<typeof SkeletonComponent> & {
  children: ReactNode;
};

const Skeleton = ({ children, className }: SkeletonProps): JSX.Element => {
  return (
    <SkeletonComponent
      className={cn(
        'animation-none grid h-[400px] place-items-center',
        className,
      )}
    >
      {children}
    </SkeletonComponent>
  );
};

export default Skeleton;
