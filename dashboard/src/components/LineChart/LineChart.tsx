import type { ComponentProps, ReactElement, JSX } from 'react';
import { LineChart as LineChartComponent } from '@mui/x-charts/LineChart';

import { axisClasses } from '@mui/x-charts/ChartsAxis/axisClasses';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

interface ILineChartLabel {
  text: string;
  backgroundColor: string;
}

export const LineChartLabel = ({
  text,
  backgroundColor,
}: ILineChartLabel): JSX.Element => {
  return (
    <div className="flex items-center gap-2 pr-6 font-medium text-gray-700">
      <ColoredCircle
        className="h-3 w-3"
        backgroundClassName={backgroundColor}
      />
      <span>{text}</span>
    </div>
  );
};

type MUILineChart = typeof LineChartComponent;
type MUILineChartProps = ComponentProps<MUILineChart>;

export type TLineChartProps = {
  labels?: ReactElement;
  series: MUILineChartProps['series'];
  xAxis: MUILineChartProps['xAxis'];
  sx?: MUILineChartProps['sx'];
  onMarkClick?: MUILineChartProps['onMarkClick'];
  slots?: MUILineChartProps['slots'];
  slotProps?: MUILineChartProps['slotProps'];
};

export const LineChart = ({
  labels,
  series,
  xAxis,
  slots,
  slotProps,
  sx,
  onMarkClick,
}: TLineChartProps): JSX.Element => {
  return (
    <div className="px-4">
      {/* {labels && (
        <div className="mt-3 mb-0 flex justify-end gap-2">{labels}</div>
      )} */}
      <LineChartComponent
        className="w-full"
        xAxis={xAxis}
        // xAxis={[{ data: [1, 2, 3, 4, 5] }]}
        // sx={sx}
        slots={slots}
        // slotProps={{ axisLabel: { className: 'font-red' } }}
        sx={_ => ({
          [`.${axisClasses.root}`]: {
            [`.${axisClasses.tickLabel}`]: {
              fontSize: '15px !important',
            },
          },
        })}
        series={series}
        // series={[{ data: [1, 5, 3, 10] }, {data: [2, 4, 4, 5]}]}
        onMarkClick={onMarkClick}
        height={300}
      />
    </div>
  );
};
