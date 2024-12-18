import { memo, useMemo } from 'react';

import { Badge } from '@/components/ui/badge';

import BaseCard, { type IBaseCard } from './BaseCard';

interface ICompatible {
  title: IBaseCard['title'];
  compatibles: string[];
}

const CompatibleHardware = ({
  title,
  compatibles,
}: ICompatible): JSX.Element => {
  const compatiblesSorted = useMemo(() => compatibles.sort(), [compatibles]);

  return (
    <BaseCard
      title={title}
      className="mb-0"
      content={
        <div className="flex flex-row flex-wrap gap-4 p-4">
          {compatiblesSorted.map(compatible => (
            <Badge
              key={compatible}
              variant="outline"
              className="text-sm font-normal"
            >
              {compatible}
            </Badge>
          ))}
        </div>
      }
    />
  );
};

export default memo(CompatibleHardware);
