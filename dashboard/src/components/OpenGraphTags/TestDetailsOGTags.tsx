import type { JSX } from 'react';
import { memo, useMemo } from 'react';

import { useIntl } from 'react-intl';

import type { TTestDetails } from '@/types/tree/TestDetails';

import { getTestHardware } from '@/lib/test';

import { OpenGraphTags } from './OpenGraphTags';

const TestDetailsOGTags = ({
  title,
  data,
}: {
  title: string;
  data?: TTestDetails;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const testDetailsDescription: string = useMemo(() => {
    if (!data) {
      return formatMessage({ id: 'test.details' });
    }

    const statusDescription =
      formatMessage({ id: 'global.status' }) + ': ' + data.status;

    const hardwareDescription =
      formatMessage({ id: 'global.hardware' }) +
      ': ' +
      getTestHardware({
        misc: data.environment_misc,
        compatibles: data.environment_compatible,
        defaultValue: formatMessage({ id: 'global.unknown' }),
      });

    const treeDescription =
      formatMessage({ id: 'global.treeBranch' }) +
      ': ' +
      data.tree_name +
      ' / ' +
      data.git_repository_branch;

    const descriptionChunks = [
      statusDescription,
      treeDescription,
      hardwareDescription,
    ];

    return descriptionChunks.join(';\n');
  }, [data, formatMessage]);

  return <OpenGraphTags title={title} description={testDetailsDescription} />;
};

export const MemoizedTestDetailsOGTags = memo(TestDetailsOGTags);
