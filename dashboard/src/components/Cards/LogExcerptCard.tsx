import { FormattedMessage } from 'react-intl';

import type { TTestDetails } from '@/types/tree/TestDetails';

import BaseCard from '@/components/Cards/BaseCard';

import CodeBlock from '@/components/Filter/CodeBlock';

type TTestDetailsDefaultProps = {
  data: TTestDetails;
};

const LogExcerpt = ({ data }: TTestDetailsDefaultProps): JSX.Element => {
  return (
    <BaseCard
      title={<FormattedMessage id="testDetails.logExcerpt" />}
      className="gap-0"
      content={<CodeBlock code={data.log_excerpt ?? ''} />}
    />
  );
};

export default LogExcerpt;
