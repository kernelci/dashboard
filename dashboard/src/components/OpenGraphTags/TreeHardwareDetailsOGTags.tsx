import { useIntl, type IntlFormatters } from 'react-intl';

import { memo, useMemo, type JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';
import type { GroupedStatus } from '@/utils/status';

import { OpenGraphTags } from './OpenGraphTags';

const getCounterDescription = ({
  tabCount,
  formatMessage,
}: {
  tabCount: GroupedStatus;
  formatMessage: IntlFormatters['formatMessage'];
}): string => {
  const tabCounters: [MessagesKey, number][] = [
    ['tag.passCount', tabCount.successCount],
    ['tag.failCount', tabCount.failedCount],
    ['tag.inconclusiveCount', tabCount.inconclusiveCount],
  ];
  const tabChunks: string[] = [];
  tabCounters.map(([intlKey, count]) => {
    if (count > 0) {
      tabChunks.push(formatMessage({ id: intlKey }, { count: count }));
    }
  });

  return tabChunks.join(', ');
};

const TreeHardwareDetailsOGTags = ({
  title,
  buildCount,
  bootCount,
  testCount,
}: {
  title: string;
  buildCount: GroupedStatus;
  bootCount: GroupedStatus;
  testCount: GroupedStatus;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const treeDetailsDescription = useMemo(() => {
    const allCounters: [MessagesKey, string][] = [];

    const buildDescription = getCounterDescription({
      tabCount: buildCount,
      formatMessage: formatMessage,
    });
    if (buildDescription.length > 0) {
      allCounters.push(['global.builds', buildDescription]);
    }

    const bootDescription = getCounterDescription({
      tabCount: bootCount,
      formatMessage: formatMessage,
    });
    if (bootDescription.length > 0) {
      allCounters.push(['global.boots', bootDescription]);
    }

    const testDescription = getCounterDescription({
      tabCount: testCount,
      formatMessage: formatMessage,
    });
    if (testDescription.length > 0) {
      allCounters.push(['global.tests', testDescription]);
    }

    if (allCounters.length > 0) {
      const descriptionChunks: string[] = [];
      allCounters.map(([intlKey, description]) => {
        descriptionChunks.push(
          formatMessage({ id: intlKey }) + ': ' + description,
        );
      });
      return descriptionChunks.join(';\n');
    }

    return formatMessage({ id: 'tag.noBuildsOrTestsData' });
  }, [buildCount, bootCount, testCount, formatMessage]);

  return <OpenGraphTags title={title} description={treeDetailsDescription} />;
};

export const MemoizedTreeHardwareDetailsOGTags = memo(
  TreeHardwareDetailsOGTags,
);
