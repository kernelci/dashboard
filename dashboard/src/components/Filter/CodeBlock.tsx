import { GoScreenFull } from 'react-icons/go';
import { LiaInfoCircleSolid } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import type { PropsWithChildren } from 'react';
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

type TCodeBlockProps = {
  code: string;
  className?: string;
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
            className="absolute right-[20px] top-[10px] opacity-50 hover:opacity-100"
          >
            <GoScreenFull size={25} />
          </Button>
        </DialogTrigger>

        <DialogContent className="sm:max-w-[70%]">
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
  highlightedCode,
  className,
  footer,
}: {
  highlightedCode: string;
  className?: string;
  footer?: JSX.Element;
}): JSX.Element => {
  return (
    <>
      <pre
        className={cn(
          'w-full max-w-[calc(100vw_-_398px)] overflow-x-auto rounded-md bg-[#DDDDDD] p-4 font-mono text-[#767676]',
          className,
        )}
      >
        <div dangerouslySetInnerHTML={{ __html: highlightedCode }}></div>
      </pre>

      {footer}
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
            backgroundClassName="bg-lightRed"
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
            backgroundClassName="bg-mediumGray"
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
}: TCodeBlockProps): JSX.Element => {
  const highlightedCode: IHighlightedCode = useMemo(
    () => generateHighlightedCode(code),
    [code],
  );

  const footerElement =
    highlightedCode.highlightCount > 0 ? (
      <HighlightCounts
        highlightedCode={highlightedCode}
        highlightsClassnames={highlightsClassnames}
      />
    ) : undefined;

  return (
    <div>
      <div className="py-4 pl-3">
        <span className="font-bold">
          <FormattedMessage
            id="buildAccordion.logExcerpt"
            defaultMessage="Log Excerpt"
          />
        </span>
      </div>

      <CodeBlockDialog>
        <MemoizedCode
          className="max-h-[520px]"
          highlightedCode={highlightedCode.highlightedCode}
          footer={footerElement}
        />
      </CodeBlockDialog>

      <MemoizedCode
        className="max-h-[425px]"
        highlightedCode={highlightedCode.highlightedCode}
        footer={footerElement}
      />
    </div>
  );
};

export default CodeBlock;
