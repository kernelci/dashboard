import {
  Select as SelectUI,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const Select = (props: React.ComponentProps<typeof SelectUI>): JSX.Element => {
  const { children, ...propsWithoutChildren } = props;

  return (
    <SelectUI {...propsWithoutChildren}>
      <SelectTrigger className="border-dim-gray text-dim-gray w-auto rounded-full border-2 px-6 py-4 text-base font-medium">
        <SelectValue placeholder="" />
      </SelectTrigger>
      <SelectContent>{children}</SelectContent>
    </SelectUI>
  );
};

export default Select;
export { SelectItem };
