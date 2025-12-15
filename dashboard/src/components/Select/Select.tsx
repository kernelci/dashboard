import type { JSX } from 'react';

import {
  Select as SelectUI,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface SelectProps extends React.ComponentProps<typeof SelectUI> {
  'data-test-id'?: string;
}

const Select = (props: SelectProps): JSX.Element => {
  const {
    children,
    'data-test-id': dataTestId,
    ...propsWithoutChildren
  } = props;

  return (
    <SelectUI {...propsWithoutChildren}>
      <SelectTrigger
        className="border-dim-gray text-dim-gray w-auto rounded-full border-2 px-6 py-4 text-base font-medium"
        data-test-id={dataTestId}
      >
        <SelectValue placeholder="" />
      </SelectTrigger>
      <SelectContent>{children}</SelectContent>
    </SelectUI>
  );
};

export default Select;
export { SelectItem };
