import { MdExpandMore } from 'react-icons/md';

import { FormattedMessage } from 'react-intl';

import TreeDetailsTab from '@/components/Tabs/TreeDetailsTab';
import ButtonWithIcon from '@/components/Button/ButtonWithIcon';

const TreeDetails = (): JSX.Element => {
  return (
    <div className="flex flex-col pt-8">
      <div className="flex flex-row pb-2 border-b border-darkGray">
        <TreeDetailsTab />
        <ButtonWithIcon
          icon={<MdExpandMore />}
          label={<FormattedMessage id="global.filters" />}
        />
      </div>
    </div>
  );
};

export default TreeDetails;
