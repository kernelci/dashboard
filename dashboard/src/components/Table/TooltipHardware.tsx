import { useMemo } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { sanitizeTableValue } from '@/components/Table/tableUtils';

const tooltipStartIdx = 1;

const TooltipHardware = ({
  hardwares,
}: {
  hardwares: string[] | undefined;
}): JSX.Element => {
  const shouldHaveTooltip = hardwares && hardwares.length > 1;

  const hardwaresTooltip = useMemo(() => {
    return shouldHaveTooltip
      ? hardwares.slice(tooltipStartIdx).map(hardware => (
          <div key={hardware} className="text-center">
            <span>{hardware}</span>
            <br />
          </div>
        ))
      : '-';
  }, [hardwares, shouldHaveTooltip]);

  const hardwareTrigger = sanitizeTableValue(hardwares?.[0], false);

  if (!shouldHaveTooltip) {
    return <span>{hardwareTrigger}</span>;
  }

  return (
    <Tooltip>
      <TooltipTrigger>{hardwareTrigger}</TooltipTrigger>
      <TooltipContent>{hardwaresTooltip}</TooltipContent>
    </Tooltip>
  );
};

export default TooltipHardware;
