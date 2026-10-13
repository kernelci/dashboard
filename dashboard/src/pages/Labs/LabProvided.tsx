import type { JSX } from 'react';

import { PieChart } from '@mui/x-charts/PieChart';
import { FormattedMessage, useIntl } from 'react-intl';

import { BaseCard } from '@/components/Cards/BaseCard';
import { Colors } from '@/components/StatusChart/StatusCharts';

import type { MessagesKey } from '@/locales/messages';
import type { Status } from '@/types/database';
import type { RequiredStatusCount } from '@/types/general';

import {
  fillCount,
  fillTone,
  frequencySlices,
  type FillTone,
  type FrequencySlice,
  type LabBootRow,
  type LabBuildRow,
  type LabTestRow,
} from './labDetailsMock';

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

const UNKNOWN_COLOR = '#EAEAEA';
const OTHER_COLOR = '#9CA3AF';
const PERCENT = 100;

const sliceColor = (slice: FrequencySlice, index: number): string => {
  if (slice.kind === 'unknown') {
    return UNKNOWN_COLOR;
  }
  if (slice.kind === 'other') {
    return OTHER_COLOR;
  }
  return SLICE_COLORS[index % SLICE_COLORS.length] ?? SLICE_COLORS[0];
};

const sliceLabel = (
  slice: FrequencySlice,
  formatMessage: (descriptor: { id: MessagesKey }) => string,
): string => {
  if (slice.kind === 'unknown') {
    return formatMessage({ id: 'global.unknown' });
  }
  if (slice.kind === 'other') {
    return formatMessage({ id: 'labDetails.other' });
  }
  return slice.name;
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
  const percent = total === 0 ? 0 : Math.round((PERCENT * filled) / total);
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
  labels,
}: {
  titleId: MessagesKey;
  labels: readonly string[];
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const slices = frequencySlices(labels).map((slice, index) => ({
    value: slice.value,
    label: sliceLabel(slice, formatMessage),
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
  const slices = STATUS_ORDER.flatMap(status => {
    const value = counts[status];
    if (value === 0) {
      return [];
    }
    return [
      {
        label: formatMessage({ id: STATUS_LABEL[status] }),
        value,
        color: STATUS_COLOR[status],
      },
    ];
  });

  return <Donut titleId={titleId} slices={slices} testId="lab-status-chart" />;
};

const sentLabels = (labels: readonly string[]): string[] =>
  labels.filter(label => label.trim() !== '');

const LabProvided = ({
  builds,
  boots,
  tests,
  buildCounts,
  bootCounts,
  testCounts,
  checkoutTotal,
  checkoutsBuilt,
  checkoutsBooted,
  checkoutsTested,
}: {
  builds: LabBuildRow[];
  boots: LabBootRow[];
  tests: LabTestRow[];
  buildCounts: RequiredStatusCount;
  bootCounts: RequiredStatusCount;
  testCounts: RequiredStatusCount;
  checkoutTotal: number;
  checkoutsBuilt: number;
  checkoutsBooted: number;
  checkoutsTested: number;
}): JSX.Element => {
  const runs = [...boots, ...tests];
  const duration = fillCount(runs.map(row => row.hasDuration));
  const fullLog = fillCount(runs.map(row => row.hasLogUrl));
  const excerpt = fillCount(runs.map(row => row.hasLogExcerpt));
  const buildDuration = fillCount(builds.map(row => row.hasDuration));
  const platform = fillCount(runs.map(row => row.platform.trim() !== ''));

  return (
    <div className="flex flex-col gap-2">
      <BaseCard
        title={<FormattedMessage id="labDetails.submissionFill" />}
        content={
          <div className="grid grid-cols-2 gap-4 px-4 pb-4 sm:grid-cols-4">
            <FillStat
              labelId="labDetails.checkoutsBuilt"
              filled={checkoutsBuilt}
              total={checkoutTotal}
            />
            <FillStat
              labelId="labDetails.checkoutsBooted"
              filled={checkoutsBooted}
              total={checkoutTotal}
            />
            <FillStat
              labelId="labDetails.checkoutsTested"
              filled={checkoutsTested}
              total={checkoutTotal}
            />
            <FillStat
              labelId="labDetails.duration"
              filled={duration.filled}
              total={duration.total}
            />
            {builds.length > 0 ? (
              <FillStat
                labelId="labDetails.buildDuration"
                filled={buildDuration.filled}
                total={buildDuration.total}
              />
            ) : null}
            <FillStat
              labelId="global.platform"
              filled={platform.filled}
              total={platform.total}
            />
            <FillStat
              labelId="labDetails.fullLog"
              filled={fullLog.filled}
              total={fullLog.total}
            />
            <FillStat
              labelId="labDetails.logExcerpt"
              filled={excerpt.filled}
              total={excerpt.total}
            />
          </div>
        }
      />
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
                labels={sentLabels(runs.map(row => row.platform))}
              />
              <FrequencyChart
                titleId="global.config"
                labels={sentLabels(runs.map(row => row.config))}
              />
              <FrequencyChart
                titleId="global.compiler"
                labels={sentLabels(runs.map(row => row.compiler))}
              />
              <FrequencyChart
                titleId="global.architecture"
                labels={sentLabels(runs.map(row => row.arch))}
              />
              {builds.length > 0 ? (
                <StatusChart
                  titleId="buildTab.buildStatus"
                  counts={buildCounts}
                />
              ) : null}
              <StatusChart titleId="bootsTab.bootStatus" counts={bootCounts} />
              <StatusChart titleId="testsTab.testStatus" counts={testCounts} />
            </div>
          </div>
        }
      />
    </div>
  );
};

export default LabProvided;
