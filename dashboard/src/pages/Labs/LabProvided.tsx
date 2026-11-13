import type { JSX } from 'react';

import { PieChart } from '@mui/x-charts/PieChart';
import { FormattedMessage, useIntl } from 'react-intl';

import { BaseCard } from '@/components/Cards/BaseCard';
import { Colors } from '@/components/StatusChart/StatusCharts';

import type { MessagesKey } from '@/locales/messages';
import type { Status } from '@/types/database';
import type { RequiredStatusCount } from '@/types/general';
import type { LabDistribution, LabFill } from '@/types/labDetails';

import { toStatusCount } from './labDetails';

const FREQUENCY_TOP = 8;
const FILL_GREEN_AT = 80;
const FILL_YELLOW_AT = 50;
const PERCENT = 100;

type FrequencySlice =
  | { kind: 'named'; name: string; value: number }
  | { kind: 'other'; value: number };

type FillTone = 'good' | 'mid' | 'bad';

const frequencySlices = (
  counts: { name: string; count: number }[],
): FrequencySlice[] => {
  const named = counts.filter(item => item.name !== '');
  const slices: FrequencySlice[] = named.slice(0, FREQUENCY_TOP).map(item => ({
    kind: 'named',
    name: item.name,
    value: item.count,
  }));
  const other = named
    .slice(FREQUENCY_TOP)
    .reduce((sum, item) => sum + item.count, 0);
  if (other > 0) {
    slices.push({ kind: 'other', value: other });
  }
  return slices;
};

const fillPercent = (filled: number, total: number): number =>
  total === 0 ? 0 : Math.round((filled / total) * PERCENT);

const fillTone = (percent: number): FillTone => {
  if (percent >= FILL_GREEN_AT) {
    return 'good';
  }
  if (percent >= FILL_YELLOW_AT) {
    return 'mid';
  }
  return 'bad';
};

const SLICE_COLORS = [
  '#4C78A8',
  '#F58518',
  '#54A24B',
  '#E45756',
  '#72B7B2',
  '#EECA3B',
  '#B279A2',
  '#FF9DA6',
];

const OTHER_COLOR = '#9CA3AF';

const sliceColor = (slice: FrequencySlice, index: number): string => {
  if (slice.kind === 'other') {
    return OTHER_COLOR;
  }
  return SLICE_COLORS[index % SLICE_COLORS.length] ?? SLICE_COLORS[0];
};

const TONE_CLASS: Record<FillTone, string> = {
  good: 'text-green',
  mid: 'text-[#EAB839]',
  bad: 'text-red',
};

const FillStat = ({
  labelId,
  filled,
  total,
}: {
  labelId: MessagesKey;
  filled: number;
  total: number;
}): JSX.Element => {
  const percent = fillPercent(filled, total);
  const tone = fillTone(percent);

  return (
    <div data-test-id="lab-fill-stat" data-tone={tone}>
      <div className="text-sm text-gray-500">
        <FormattedMessage id={labelId} />
      </div>
      <div className={`text-2xl font-semibold ${TONE_CLASS[tone]}`}>
        {percent}%
      </div>
      <div className="text-sm">
        <FormattedMessage id="labDetails.fillOf" values={{ filled, total }} />
      </div>
    </div>
  );
};

type DonutSlice = {
  label: string;
  value: number;
  color: string;
};

const Donut = ({
  titleId,
  slices,
  testId,
}: {
  titleId: MessagesKey;
  slices: DonutSlice[];
  testId: string;
}): JSX.Element => {
  const total = slices.reduce((sum, slice) => sum + slice.value, 0);
  const data = slices.map((slice, index) => ({ id: index, ...slice }));

  return (
    <div data-test-id={testId}>
      <div className="mb-2 font-medium">
        <FormattedMessage id={titleId} />
      </div>
      {total === 0 ? (
        <p className="text-sm text-gray-500">
          <FormattedMessage id="global.noResults" />
        </p>
      ) : (
        <div className="flex min-w-0 items-start gap-2">
          <div className="relative h-[120px] w-[120px] shrink-0">
            <PieChart
              series={[
                {
                  data,
                  innerRadius: 36,
                  outerRadius: 56,
                },
              ]}
              height={120}
              width={120}
              margin={{ top: 0, bottom: 0, left: 0, right: 0 }}
              slotProps={{ legend: { hidden: true } }}
            />
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center text-xs font-semibold">
              {total}
            </div>
          </div>
          <ul className="min-w-0 text-xs">
            {data.map(item => (
              <li key={item.id} className="flex items-center">
                <span
                  className="mr-1 inline-block h-2 w-2 shrink-0 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="truncate">{item.label}</span>
                <span className="ml-[2em] shrink-0 tabular-nums">
                  {item.value}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const FrequencyChart = ({
  titleId,
  counts,
}: {
  titleId: MessagesKey;
  counts: LabDistribution['platforms'];
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const slices = frequencySlices(counts).map((slice, index) => ({
    value: slice.value,
    label:
      slice.kind === 'other'
        ? formatMessage({ id: 'labDetails.other' })
        : slice.name,
    color: sliceColor(slice, index),
  }));

  return (
    <Donut titleId={titleId} slices={slices} testId="lab-frequency-chart" />
  );
};

const STATUS_ORDER = [
  'PASS',
  'FAIL',
  'ERROR',
  'MISS',
  'SKIP',
  'DONE',
  'NULL',
] as const satisfies readonly Status[];

const STATUS_COLOR: Record<Status, string> = {
  PASS: Colors.Green,
  FAIL: Colors.Red,
  ERROR: '#F58518',
  MISS: '#B279A2',
  SKIP: '#72B7B2',
  DONE: '#4C78A8',
  NULL: Colors.Gray,
};

const STATUS_LABEL: Record<Status, MessagesKey> = {
  PASS: 'testStatus.pass',
  FAIL: 'testStatus.fail',
  ERROR: 'testStatus.error',
  MISS: 'testStatus.miss',
  SKIP: 'testStatus.skip',
  DONE: 'testStatus.done',
  NULL: 'testStatus.null',
};

const StatusChart = ({
  titleId,
  counts,
}: {
  titleId: MessagesKey;
  counts: RequiredStatusCount;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const slices = STATUS_ORDER.flatMap(item => {
    const value = counts[item];
    if (value === 0) {
      return [];
    }
    return [
      {
        label: formatMessage({ id: STATUS_LABEL[item] }),
        value,
        color: STATUS_COLOR[item],
      },
    ];
  });

  return <Donut titleId={titleId} slices={slices} testId="lab-status-chart" />;
};

const LabProvided = ({
  distribution,
  fill,
}: {
  distribution: LabDistribution;
  fill: LabFill;
}): JSX.Element => {
  const hasBuilds = fill.builds_total > 0;

  return (
    <div className="flex flex-col gap-2">
      <BaseCard
        title={<FormattedMessage id="labDetails.distribution" />}
        content={
          <div className="flex flex-col gap-4 px-4 pb-4">
            <p className="text-sm text-gray-600">
              <FormattedMessage id="labDetails.distributionNote" />
            </p>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <FrequencyChart
                titleId="global.platform"
                counts={distribution.platforms}
              />
              <FrequencyChart
                titleId="global.config"
                counts={distribution.configs}
              />
              <FrequencyChart
                titleId="global.compiler"
                counts={distribution.compilers}
              />
              <FrequencyChart
                titleId="global.architecture"
                counts={distribution.architectures}
              />
              {hasBuilds ? (
                <StatusChart
                  titleId="buildTab.buildStatus"
                  counts={toStatusCount(distribution.build_status)}
                />
              ) : null}
              <StatusChart
                titleId="bootsTab.bootStatus"
                counts={toStatusCount(distribution.boot_status)}
              />
              <StatusChart
                titleId="testsTab.testStatus"
                counts={toStatusCount(distribution.test_status)}
              />
            </div>
          </div>
        }
      />
      <BaseCard
        title={<FormattedMessage id="labDetails.submissionFill" />}
        content={
          <div className="grid grid-cols-2 gap-4 px-4 pb-4 sm:grid-cols-4">
            <FillStat
              labelId="labDetails.checkoutsBuilt"
              filled={fill.checkouts_built}
              total={fill.checkout_total}
            />
            <FillStat
              labelId="labDetails.checkoutsBooted"
              filled={fill.checkouts_booted}
              total={fill.checkout_total}
            />
            <FillStat
              labelId="labDetails.checkoutsTested"
              filled={fill.checkouts_tested}
              total={fill.checkout_total}
            />
            <FillStat
              labelId="labDetails.duration"
              filled={fill.runs_with_duration}
              total={fill.runs_total}
            />
            {hasBuilds ? (
              <FillStat
                labelId="labDetails.buildDuration"
                filled={fill.builds_with_duration}
                total={fill.builds_total}
              />
            ) : null}
            <FillStat
              labelId="global.platform"
              filled={fill.runs_with_platform}
              total={fill.runs_total}
            />
            <FillStat
              labelId="labDetails.fullLog"
              filled={fill.runs_with_log_url}
              total={fill.runs_total}
            />
            <FillStat
              labelId="labDetails.logExcerpt"
              filled={fill.runs_with_log_excerpt}
              total={fill.runs_total}
            />
          </div>
        }
      />
    </div>
  );
};

export default LabProvided;
