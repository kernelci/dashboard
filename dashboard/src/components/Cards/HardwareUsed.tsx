import { memo, useMemo } from 'react';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';

import { Badge } from '@/components/ui/badge';

interface IHardwareUsed {
  title: IBaseCard['title'];
  hardwareUsed?: string[];
}

const HardwareUsed = ({ hardwareUsed, title }: IHardwareUsed): JSX.Element => {
  const hardwareSorted = useMemo(() => {
    return hardwareUsed?.sort().map(hardware => {
      return (
        <Badge key={hardware} variant="outline" className="text-sm font-normal">
          {hardware}
        </Badge>
      );
    });
  }, [hardwareUsed]);

  return (
    <BaseCard
      title={title}
      content={
        <div className="flex flex-row flex-wrap gap-4 p-4">
          {hardwareSorted}
        </div>
      }
    />
  );
};

export default memo(HardwareUsed);
