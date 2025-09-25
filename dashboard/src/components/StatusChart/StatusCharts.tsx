import { PieChart } from '@mui/x-charts/PieChart';

import { MdArrowDownward, MdArrowUpward } from 'react-icons/md';
import type { ReactElement, JSX } from 'react';
import React, { useMemo } from 'react';

import { useDrawingArea } from '@mui/x-charts';
import { styled } from '@mui/material';

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
  Yellow = '#FFD27C',
  Gray = '#EAEAEA',
  Blue = '#11B3E6',
  DimGray = '454545',
}

export interface IStatusChart {
  onLegendClick?: (value: string) => void;
  elements: StatusChartValues[];
  insideText?: StatusChartValues;
  increaseElement?: StatusChartValues;
  decreaseElement?: StatusChartValues;
  pieCentralLabel?: string;
  pieCentralDescription?: ReactElement;
  title?: ReactElement;
  type: 'chart';
}

interface IChartLegend {
  onClick?: (value: string) => void;
  chartValues: (StatusChartValues | undefined)[];
}

interface IRegressionElement {
  element: StatusChartValues;
  icon: ReactElement;
}

interface IRegressionStatus {
  increaseElement?: StatusChartValues;
  decreaseElement?: StatusChartValues;
}

const StatusChart = ({
  elements,
  increaseElement,
  decreaseElement,
  pieCentralLabel,
  pieCentralDescription,
  title,
  onLegendClick,
}: IStatusChart): JSX.Element => {
  const showChart = elements.some(element => element.value > 0);

  const dataSeries = useMemo(() => {
    return [
      {
        data: elements.map(element => ({
          ...element,
          label: '',
        })),
        innerRadius: 50,
        outerRadius: 80,
        cx: 80,
        cy: 80,
      },
    ];
  }, [elements]);

  if (!showChart) {
    return <></>;
  }
  return (
    <div className="p-4">
      <span className="font-bold">{title}</span>
      <div className="flex flex-col items-center sm:flex-row">
        <PieChart
          series={dataSeries}
          height={170}
          width={170}
          slotProps={{
            legend: {
              hidden: true,
            },
          }}
        >
          <PieCenterLabel
            label={pieCentralLabel ?? ''}
            description={pieCentralDescription ?? <></>}
          />
        </PieChart>
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-end">
          <ChartLegend chartValues={elements} onClick={onLegendClick} />
          <RegressionsStatus
            increaseElement={increaseElement}
            decreaseElement={decreaseElement}
          />
        </div>
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
    case Colors.Yellow:
      return 'bg-yellow';
    case Colors.Gray:
      return 'bg-medium-gray';
    case Colors.DimGray:
      return 'bg-dim-gray';
    case Colors.Blue:
      return 'bg-blue';
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

const RegressionsStatus = ({
  increaseElement,
  decreaseElement,
}: IRegressionStatus): JSX.Element => {
  return (
    <div className="flex flex-col gap-2">
      {increaseElement && (
        <RegressionElement
          element={increaseElement}
          icon={<MdArrowUpward color={Colors.Red} />}
        />
      )}
      {decreaseElement && (
        <RegressionElement
          element={decreaseElement}
          icon={<MdArrowDownward color={Colors.Green} />}
        />
      )}
    </div>
  );
};

const RegressionElement = ({
  element,
  icon,
}: IRegressionElement): JSX.Element => {
  return (
    <div className="flex flex-row gap-2">
      <div className="pt-1">{icon}</div>
      <div className="flex flex-col gap-1">
        <span className="font-bold">{element.value}</span>
        <span>{element.label}</span>
      </div>
    </div>
  );
};

const PieCenterLabel = ({
  label,
  description,
}: {
  label: string;
  description: ReactElement;
}): JSX.Element => {
  const { width, height, left, top } = useDrawingArea();
  // eslint-disable-next-line no-magic-numbers
  const yPositionLabel = 9 / 20;
  // eslint-disable-next-line no-magic-numbers
  const yPositionDescription = 11 / 20;
  // eslint-disable-next-line no-magic-numbers
  const xPosition = left + width * 1.3;
  return (
    <>
      <StyledText x={xPosition} y={top + yPositionLabel * height}>
        {label}
      </StyledText>
      <StyledText
        sx={{
          fontWeight: 'bold',
        }}
        x={xPosition}
        y={top + yPositionDescription * height}
      >
        {description}
      </StyledText>
    </>
  );
};

const StyledText = styled('text')(() => ({
  textAnchor: 'middle',
  dominantBaseline: 'central',
}));

export default StatusChartMemoized;
