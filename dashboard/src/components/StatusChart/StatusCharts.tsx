import { PieChart } from '@mui/x-charts/PieChart';

import type { ReactElement, JSX } from 'react';
import React, { useMemo } from 'react';

import { useIntl } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

export type StatusChartValues = {
  value: number;
  label: MessagesKey;
  color: Colors;
};

export enum Colors {
  Red = '#E15739',
  Green = '#53D07C',
  Gray = '#EAEAEA',
}

export interface IStatusChart {
  onLegendClick?: (value: string) => void;
  elements: StatusChartValues[];
  pieCentralLabel?: string;
  pieCentralDescription?: ReactElement;
}

interface IChartLegend {
  onClick?: (value: string) => void;
  chartValues: (StatusChartValues | undefined)[];
}

const StatusChart = ({
  elements,
  pieCentralLabel,
  pieCentralDescription,
  onLegendClick,
}: IStatusChart): JSX.Element => {
  const { formatMessage } = useIntl();
  const showChart = elements.some(element => element.value > 0);

  const dataSeries = useMemo(() => {
    return [
      {
        data: elements.map(element => ({
          ...element,
          label: formatMessage({ id: element.label }),
        })),
        innerRadius: 50,
        outerRadius: 80,
      },
    ];
  }, [elements, formatMessage]);

  if (!showChart) {
    return <></>;
  }
  return (
    <div className="p-4">
      <div className="flex flex-col items-center sm:flex-row">
        <div className="flex justify-center sm:flex-1">
          <div className="relative h-[170px] w-[170px]">
            <PieChart
              series={dataSeries}
              height={170}
              width={170}
              margin={{ top: 0, bottom: 0, left: 0, right: 0 }}
              slotProps={{
                legend: {
                  hidden: true,
                },
              }}
            />
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-dark-gray2 text-sm">{pieCentralLabel}</span>
              <span className="font-bold">{pieCentralDescription}</span>
            </div>
          </div>
        </div>
        <ChartLegend chartValues={elements} onClick={onLegendClick} />
      </div>
    </div>
  );
};

const StatusChartMemoized = React.memo(StatusChart);

const getColorClassName = (color: Colors): string => {
  switch (color) {
    case Colors.Red:
      return 'bg-red';
    case Colors.Green:
      return 'bg-green';
    case Colors.Gray:
      return 'bg-medium-gray';
    default:
      return '';
  }
};

const ChartLegend = ({ chartValues, onClick }: IChartLegend): JSX.Element => {
  const intl = useIntl();
  const legend = useMemo(() => {
    return chartValues.map(chartValue => {
      const WrapperElement = onClick ? 'button' : 'div';
      const status = intl.formatMessage({ id: chartValue?.label });

      if (!chartValue?.label) {
        return (
          <div key={chartValue?.color} className="hidden">
            Invalid chart value
            <pre>{JSON.stringify(chartValue)}</pre>
          </div>
        );
      }

      return (
        chartValue.value !== 0 && (
          <WrapperElement
            onClick={(): void => onClick?.(status)}
            key={chartValue?.color}
            className="flex flex-row text-left"
          >
            {chartValue && (
              <div className="pt-1 pr-2">
                <ColoredCircle
                  backgroundClassName={getColorClassName(chartValue.color)}
                />
              </div>
            )}
            <div className="flex min-w-0 flex-col">
              <span className="font-bold">{chartValue?.value}</span>
              <span className="text-dark-gray2 text-sm">{status}</span>
            </div>
          </WrapperElement>
        )
      );
    });
  }, [chartValues, intl, onClick]);
  return (
    <div className="flex flex-row flex-wrap justify-center gap-4 sm:flex-col">
      {legend}
    </div>
  );
};

export default StatusChartMemoized;
