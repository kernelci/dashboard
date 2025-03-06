import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import { Skeleton } from '@/components/ui/skeleton';
import type { CodeBlockVariant } from '@/components/Filter/CodeBlock';
import CodeBlock from '@/components/Filter/CodeBlock';
import { cn } from '@/lib/utils';

//TODO Localize the fallback string
const FallbackLog = `
 ________________________________
/ Sorry, there is no Log Excerpt \\
\\ available for this build.      /
 --------------------------------
        \\   ^__^
         \\  (oo)\\_______
            (__)\\       )\\/\\
                ||----w |
                ||     ||`;

interface ILogExcerpt {
  isLoading?: boolean;
  logExcerpt?: string;
  variant: CodeBlockVariant;
}

export const LogExcerpt = ({
  isLoading,
  logExcerpt,
  variant = 'default',
}: ILogExcerpt): JSX.Element => {
  if (isLoading) {
    return (
      <Skeleton
        className={cn('grid h-[400px] place-items-center', {
          'flex-1': variant === 'log-viewer',
        })}
      >
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );
  }

  // Use OR instead of ?? to handle empty strings
  return <CodeBlock code={logExcerpt || FallbackLog} variant={variant} />;
};
