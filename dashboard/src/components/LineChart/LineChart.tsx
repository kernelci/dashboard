import type { ComponentProps, ReactNode, JSX } from 'react';
import { LineChart as LineChartComponent } from '@mui/x-charts/LineChart';

type MUILineChart = typeof LineChartComponent;
type MUILineChartProps = ComponentProps<MUILineChart>;

export type TLineChartProps = {
  series: MUILineChartProps['series'];
  xAxis: MUILineChartProps['xAxis'];
  sx?: MUILineChartProps['sx'];
  onMarkClick?: MUILineChartProps['onMarkClick'];
  slots?: MUILineChartProps['slots'];
  slotProps?: MUILineChartProps['slotProps'];
  height?: MUILineChartProps['height'];
  margin?: MUILineChartProps['margin'];
  isLoading?: boolean;
  children?: ReactNode;
};

const EmptyNoDataOverlay = (): null => null;

export const LineChart = ({
  series,
  xAxis,
  slots,
  slotProps,
  sx,
  height,
  margin,
  onMarkClick,
  isLoading,
  children,
}: TLineChartProps): JSX.Element => {
  const mergedSlots = {
    ...slots,
    noDataOverlay: slots?.noDataOverlay ?? EmptyNoDataOverlay,
  };

  return (
    <div className="px-4">
      <LineChartComponent
        className="w-full"
        xAxis={xAxis}
        sx={sx}
        slots={mergedSlots}
        slotProps={slotProps}
        series={series}
        onMarkClick={onMarkClick}
        height={height}
        margin={margin}
        loading={isLoading}
      >
        {children}
      </LineChartComponent>
    </div>
  );
};
