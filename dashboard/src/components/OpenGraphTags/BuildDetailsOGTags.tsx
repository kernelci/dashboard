import type { JSX } from 'react';
import { memo, useMemo } from 'react';

import { useIntl } from 'react-intl';

import { getBuildStatus } from '@/utils/utils';
import type { TBuildDetails } from '@/types/tree/BuildDetails';

import { OpenGraphTags } from './OpenGraphTags';

const BuildDetailsOGTags = ({
  descriptionTitle,
  tabTitle,
  data,
}: {
  descriptionTitle: string;
  tabTitle: string;
  data?: TBuildDetails;
}): JSX.Element => {
  const { formatMessage } = useIntl();

  const buildDetailsDescription: string = useMemo(() => {
    if (!data) {
      return formatMessage({ id: 'buildDetails.buildDetails' });
    }

    const statusDescription =
      formatMessage({ id: 'global.status' }) +
      ': ' +
      getBuildStatus(data.valid).toUpperCase();

    const treeDescription =
      formatMessage({ id: 'global.treeBranch' }) +
      ': ' +
      data.tree_name +
      ' / ' +
      data.git_repository_branch;

    const descriptionChunks = [
      descriptionTitle,
      statusDescription,
      treeDescription,
    ];

    return descriptionChunks.join(';\n');
  }, [descriptionTitle, data, formatMessage]);

  return (
    <OpenGraphTags title={tabTitle} description={buildDetailsDescription} />
  );
};

export const MemoizedBuildDetailsOGTags = memo(BuildDetailsOGTags);
