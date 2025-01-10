import { MdOutlineCopyAll } from 'react-icons/md';

import { useCallback, useState } from 'react';

import { AlertDialog, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { cn } from '@/lib/utils';

interface CopyButtonProps {
  value?: string;
}

const TIME_FEEDBACK = 400;

const CopyButton = ({ value }: CopyButtonProps): JSX.Element => {
  const [copied, setCopied] = useState(false);

  const handleClick = useCallback(() => {
    navigator.clipboard.writeText(value ?? '');
    setCopied(true);
    setTimeout(() => {
      setCopied(false);
    }, TIME_FEEDBACK);
  }, [value]);

  return (
    <AlertDialog>
      <AlertDialogTrigger
        onClick={handleClick}
        className={cn(
          'ml-2 h-[20px] w-[20px] p-[2px] align-middle text-base',
          copied ? 'animate-[ping_0.4s_cubic-bezier(0,0,0.2,1)_1]' : '',
        )}
        disabled={copied}
      >
        <MdOutlineCopyAll />
      </AlertDialogTrigger>
    </AlertDialog>
  );
};

export default CopyButton;
