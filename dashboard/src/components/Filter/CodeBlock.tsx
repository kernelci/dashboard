import { GoScreenFull } from 'react-icons/go';
import { LiaInfoCircleSolid } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import type { PropsWithChildren, JSX } from 'react';
import { memo, useMemo } from 'react';

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
          'max-h-[80%] w-full max-w-[100vw] overflow-auto rounded-md bg-[#DDDDDD] p-4 font-mono text-sm leading-4 text-[#767676]',
          className,
        )}
      >
        {disableHighlight ? (
          <>{parsedCode}</>
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

export const generateHighlightedCode = (code: string): IHighlightedCode => {
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
          new RegExp(
            [
              '.*(',
              '((\\bfailed\\s*(to|with|$|([\\b\\s:]*\\(*-*[1-9]))))', // failed to/with or failed: N
              '|',
              '(',
              '(((([1-9][0]*\\s*)|[=:])fail[s]*(?!\\s*:\\s*0))', // N fail[s] (not N fail[s]:0)
              '|',
              '(fail[s]*(([:,][\\b\\s:]*[^0\\s])|$|\\s+-[1-9]))', // fail[s]: x (not fail[s]: 0)
              ')',
              '(?![|/]))', // Not match fail flags
              ')',
            ].join(''),
            'i',
          ),
        ) !== -1
      ) {
        fails++;
        return '<span class="text-red">' + match + '</span>';
      }
      // matches error codes greater than 0 or more than 0 errors
      if (
        match.search(
          new RegExp(
            [
              '.*(',
              '([1-9][0]*\\s*error[s]*(?!\\s*:\\s*0))', // N error[s] (not N error[s]:0)
              '|',
              '(?<!Ignore\\s*)', // Not match "Ignore errors"
              '(error[s]*(([:,][\\b\\s:\\(-]*[^0\\s])|$|\\s+-[1-9]|\\s[a-z]))', // error[s]: x or error -N (not error[s]: 0)
              ')',
            ].join(''),
            'i',
          ),
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

const MAX_HIGHLIGHT_CODE_LENGTH = 6000000;

const CodeBlock = ({
  code,
  highlightsClassnames,
  variant = 'default',
  className,
}: TCodeBlockProps): JSX.Element => {
  const disableHighlight = code.length >= MAX_HIGHLIGHT_CODE_LENGTH;

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
      <div className="min-h-[300px]">
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

        {disableHighlight && (
          <span className="text-gray-500">
            <FormattedMessage id="logViewer.disabledHighlight" />
          </span>
        )}
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
          variant={variant}
          parsedCode={
            typeof parsedCode === 'string'
              ? parsedCode
              : parsedCode.highlightedCode
          }
          statsElement={statsElement}
          className={className}
        />
      </div>
    </>
  );
};

export default CodeBlock;
