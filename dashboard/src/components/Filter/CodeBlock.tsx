import { GoScreenFull } from 'react-icons/go';
import { LiaInfoCircleSolid } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import type { PropsWithChildren, JSX } from 'react';
import { memo, useMemo } from 'react';

import { useSearch } from '@tanstack/react-router';

import { cn } from '@/lib/utils';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

import { Button } from '@/components/ui/button';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { zOrigin } from '@/types/general';

export type CodeBlockVariant = 'default' | 'log-viewer';

type TCodeBlockProps = {
  code: string;
  className?: string;
  variant?: CodeBlockVariant;
  highlightsClassnames?: string;
};

interface IHighlightedCode {
  highlightedCode: string;
  highlightCount: number;
  failCount: number;
  errorCount: number;
}

const CodeBlockDialog = ({ children }: PropsWithChildren): JSX.Element => {
  return (
    <div className="relative">
      <Dialog>
        <DialogTrigger asChild className="p-2">
          <Button
            variant="outline"
            className="absolute top-[10px] right-[20px] opacity-50 hover:opacity-100"
          >
            <GoScreenFull size={25} />
          </Button>
        </DialogTrigger>

        <DialogContent className="sm:h-[90%] sm:max-w-[70%]">
          <DialogHeader>
            <DialogTitle>
              <FormattedMessage id="global.logs" />
            </DialogTitle>
          </DialogHeader>
          {children}
        </DialogContent>
      </Dialog>
    </div>
  );
};

const Code = ({
  parsedCode,
  className,
  statsElement,
  variant,
  disableHighlight,
}: {
  parsedCode: string;
  className?: string;
  statsElement?: JSX.Element;
  variant: CodeBlockVariant;
  disableHighlight?: boolean;
}): JSX.Element => {
  return (
    <>
      {variant === 'log-viewer' && statsElement}
      <pre
        className={cn(
          'w-full max-w-[100vw] overflow-x-auto rounded-md bg-[#DDDDDD] p-4 font-mono text-sm leading-4 text-[#767676]',
          className,
        )}
      >
        {disableHighlight ? (
          <>parsedCode</>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: parsedCode }}></div>
        )}
      </pre>

      {variant !== 'log-viewer' && statsElement}
    </>
  );
};
const MemoizedCode = memo(Code);

const HighlightCounts = ({
  highlightsClassnames,
  highlightedCode,
}: {
  highlightsClassnames?: string;
  highlightedCode: IHighlightedCode;
}): JSX.Element => {
  return (
    <div className="py-4 pl-3">
      <ul className={cn('flex gap-2 pb-2', highlightsClassnames)}>
        <li>
          <span className="flex gap-1">
            <span className="font-bold">
              <FormattedMessage
                id="codeBlock.highlights"
                defaultMessage={'Highlights:'}
              />
            </span>
          </span>
        </li>
        <li className="flex gap-1">
          <ColoredCircle
            quantity={highlightedCode.failCount}
            backgroundClassName="bg-light-red"
          />
          <FormattedMessage id="global.fails" defaultMessage={'Fails'} />
        </li>
        <li className="flex gap-1">
          <ColoredCircle
            quantity={highlightedCode.errorCount}
            backgroundClassName="bg-orange-200"
          />
          <FormattedMessage id="global.errors" defaultMessage={'Errors'} />
        </li>
        <li className="flex gap-1">
          <ColoredCircle
            quantity={
              highlightedCode.highlightCount -
              highlightedCode.failCount -
              highlightedCode.errorCount
            }
            backgroundClassName="bg-medium-gray"
          />
          <FormattedMessage id="global.others" defaultMessage={'Others'} />
        </li>
      </ul>
      <div className="flex items-center">
        <LiaInfoCircleSolid />
        <p className="pl-1 text-sm">
          <FormattedMessage
            id="codeBlock.highlightsTooltip"
            defaultMessage="Test"
          />
        </p>
      </div>
    </div>
  );
};

const generateHighlightedCode = (code: string): IHighlightedCode => {
  let highlights = 0;
  let fails = 0;
  let errors = 0;

  // matches any < or > and replaces with equivalent &lt or &gt
  let newCode = code.replace(/[<>]/gm, match => {
    match = match.replace(/</, '&lt');
    match = match.replace(/>/, '&gt');
    return match;
  });

  newCode = newCode.replace(
    // matches any line with the occurrence of error or fail
    /^.*(error|fail).*$/gim,
    match => {
      highlights++;
      if (
        // matches failed to/with, more than 0 fails/failed and no flags
        match.search(
          /.*((\bfailed(\s*to|\s*with|([\b\s:]\s*\(*-*[1-9])))|fail(\b|:|\s*[1-9])(?![|/]))/i,
        ) !== -1
      ) {
        fails++;
        return '<span class="text-red">' + match + '</span>';
      }
      // matches error codes greater than 0 or more than 0 errors
      if (
        match.search(
          /(error(:|,|[\b\s:]\s*\(*-*[1-9a-z]))|([1-9]\s*error)/i,
        ) !== -1
      ) {
        errors++;
        return '<span class="text-orange-500">' + match + '</span>';
      }
      return '<span class="text-sky-600">' + match + '</span>';
    },
  );
  return {
    highlightedCode: newCode,
    highlightCount: highlights,
    failCount: fails,
    errorCount: errors,
  };
};

const CodeBlock = ({
  code,
  highlightsClassnames,
  variant = 'default',
}: TCodeBlockProps): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });

  const parsedOrigin = zOrigin.parse(unsafeOrigin);
  // TODO Disable highlight based on filesize
  const disableHighlight =
    parsedOrigin === 'redhat' && variant === 'log-viewer';

  const parsedCode: IHighlightedCode | string = useMemo(() => {
    if (disableHighlight) {
      return code;
    }

    return generateHighlightedCode(code);
  }, [code, disableHighlight]);

  const statsElement =
    !disableHighlight &&
    typeof parsedCode !== 'string' &&
    parsedCode.highlightCount > 0 ? (
      <HighlightCounts
        highlightedCode={parsedCode}
        highlightsClassnames={highlightsClassnames}
      />
    ) : undefined;

  return (
    <>
      <div className="h-full">
        <div className="pl-3">
          {variant === 'log-viewer' && (
            <h3 className="py-1 text-2xl font-bold">
              <FormattedMessage
                id="global.fullLogs"
                defaultMessage="Log Excerpt"
              />
            </h3>
          )}
          {variant === 'default' && (
            <h3 className="py-4 font-bold">
              <FormattedMessage
                id="global.logExcerpt"
                defaultMessage="Log Excerpt"
              />
            </h3>
          )}
        </div>

        {variant !== 'log-viewer' && (
          <CodeBlockDialog>
            <MemoizedCode
              className="max-h-[100%]"
              parsedCode={
                typeof parsedCode === 'string'
                  ? parsedCode
                  : parsedCode.highlightedCode
              }
              statsElement={statsElement}
              variant={variant}
            />
          </CodeBlockDialog>
        )}

        <MemoizedCode
          className={cn('', {
            'max-h-[425px]': variant !== 'log-viewer',
          })}
          variant={variant}
          parsedCode={
            typeof parsedCode === 'string'
              ? parsedCode
              : parsedCode.highlightedCode
          }
          statsElement={statsElement}
        />
      </div>
    </>
  );
};

export default CodeBlock;
