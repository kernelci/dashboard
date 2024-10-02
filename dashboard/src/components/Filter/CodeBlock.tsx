import { cn } from '@/lib/utils';

type TCodeBlockProps = {
  code: string;
  className?: string;
};

const CodeBlock = ({ code, className }: TCodeBlockProps): JSX.Element => {
  return (
    <pre
      className={cn(
        'max-h-[275px] w-full max-w-[calc(100vw_-_398px)] overflow-x-auto bg-[#DDDDDD] p-4 font-mono text-[#767676]',
        className,
      )}
    >
      {code}
    </pre>
  );
};

export default CodeBlock;
