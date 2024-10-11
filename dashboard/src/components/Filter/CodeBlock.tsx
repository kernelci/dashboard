import { LiaInfoCircleSolid } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import { useMemo } from 'react';

import { cn } from '@/lib/utils';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { formattedBreakLineValue } from '@/locales/messages';

type TCodeBlockProps = {
  code: string;
  className?: string;
  highlightsClassname?: string;
};

interface IHighlightedCode {
  highlightedCode: string;
  highlightCount: number;
  failCount: number;
  errorCount: number;
}

const CodeBlock = ({
  code,
  className,
  highlightsClassname,
}: TCodeBlockProps): JSX.Element => {
  const highlightedCode: IHighlightedCode = useMemo(() => {
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
          // matches failed to/with, more than 0 fails/faileds and no flags
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
  }, [code]);

  return (
    <div>
      <pre
        className={cn(
          'max-h-[275px] w-full max-w-[calc(100vw_-_398px)] overflow-x-auto bg-[#DDDDDD] p-4 font-mono text-[#767676]',
          className,
        )}
      >
        <div
          dangerouslySetInnerHTML={{ __html: highlightedCode.highlightedCode }}
        ></div>
      </pre>
      {highlightedCode.highlightCount > 0 && (
        <ul className={cn('flex gap-2 py-4 pl-3', highlightsClassname)}>
          <li>
            <span className="flex items-center gap-1">
              <Tooltip>
                <TooltipTrigger>
                  <LiaInfoCircleSolid />
                </TooltipTrigger>
                <TooltipContent>
                  <FormattedMessage
                    id="codeBlock.highlightsTooltip"
                    defaultMessage={
                      'Highlighted items accounts for any lines citing fails or errors.{br}' +
                      'That includes real failures, real errors and other information messages containing those words.'
                    }
                    values={formattedBreakLineValue}
                  />
                </TooltipContent>
              </Tooltip>
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
      )}
    </div>
  );
};

export default CodeBlock;
