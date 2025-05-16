import { MdOutlineCopyAll } from 'react-icons/md';

import { useCallback, useState, type JSX } from 'react';

import { cn } from '@/lib/utils';

import { Button } from '@/components/ui/button';

interface CopyButtonProps {
  value?: string;
}

const CopyButton = ({ value }: CopyButtonProps): JSX.Element => {
  const [copied, setCopied] = useState(false);

  const handleClick = useCallback(() => {
    navigator.clipboard.writeText(value ?? '');
    setCopied(true);
  }, [value]);

  const onAnimationEnd = useCallback(() => setCopied(false), [setCopied]);

  return (
    <Button
      variant={'ghost'}
      onClick={handleClick}
      className={cn(
        'ml-2 h-[20px] w-[20px] p-[2px] align-middle text-base',
        copied ? 'animate-[ping_0.2s_cubic-bezier(0,0,0.2,1)_1]' : '',
      )}
      onAnimationEnd={onAnimationEnd}
      disabled={copied}
      type="button"
    >
      <MdOutlineCopyAll />
    </Button>
  );
};

export default CopyButton;
