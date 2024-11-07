import { useMemo } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { sanitizeTableValue } from '@/components/Table/tableUtils';

const TooltipHardware = ({
  hardwares,
}: {
  hardwares: string[] | undefined;
}): JSX.Element => {
  const hardwaresTooltip = useMemo(() => {
    return hardwares
      ? hardwares.map(hardware => (
          <div key={hardware} className="text-center">
            <span>{hardware}</span>
            <br />
          </div>
        ))
      : '-';
  }, [hardwares]);

  return (
    <Tooltip>
      <TooltipTrigger>
        {sanitizeTableValue(hardwares?.[0], false)}
      </TooltipTrigger>
      <TooltipContent>{hardwaresTooltip}</TooltipContent>
    </Tooltip>
  );
};

export default TooltipHardware;
