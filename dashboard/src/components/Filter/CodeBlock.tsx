import { LiaInfoCircleSolid } from 'react-icons/lia';

import { FormattedMessage } from 'react-intl';

import { cn } from '@/lib/utils';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

type TCodeBlockProps = {
  code: string;
  highlightsClassname?: string;
};

const CodeBlock = ({
  code,
  highlightsClassname,
}: TCodeBlockProps): JSX.Element => {
  let highlightCount = 0;
  let failCount = 0;
  let errorCount = 0;

  // removes unwanted HTML tags
  code = code.replace(/(<|>)/gm, match => {
    match = match.replace(/</, '&lt');
    match = match.replace(/>/, '&gt');
    return match;
  });

  // highlights fails and errors
  code = code.replace(
    /^.*((\berror(:|\s*-*[0-9]|))|(\bfailed(\sto|\swith|\b|:|\s*[0-9]))|(fail(\b|[0-9]))).*$/gim,
    match => {
      highlightCount++;
      if (match.search(/fail/i) !== -1) {
        // ignores .failed files and fail flags
        if (match.search(/(\.+failed|failed(\s*0)+|[|/]fail\b)/i) !== -1) {
          return '<span class="text-blue">' + match + '</span>';
        }
        failCount++;
        return '<span class="text-red">' + match + '</span>';
      } else {
        // ignores error flags
        if (match.search(/((0\s*\t*)+error|error"+)/i) !== -1) {
          return '<span class="text-sky-600">' + match + '</span>';
        }
        errorCount++;
        return '<span class="text-orange-500">' + match + '</span>';
      }
    },
  );

  return (
    <div>
      <pre className="max-h-[275px] w-full max-w-[calc(100vw_-_398px)] overflow-x-auto bg-[#DDDDDD] p-4 font-mono text-[#767676]">
        <div dangerouslySetInnerHTML={{ __html: code }}></div>
      </pre>
      {highlightCount > 0 ? (
        <ul className={cn('flex gap-2 py-4 pl-3', highlightsClassname)}>
          <li>
            <span className="flex items-center gap-1 font-bold">
              <Tooltip>
                <TooltipTrigger>
                  <LiaInfoCircleSolid />
                </TooltipTrigger>
                <TooltipContent>
                  <FormattedMessage
                    id="codeBlock.highlightsTooltip"
                    defaultMessage={
                      'Highlighted items accounts for any lines citing fails or errors.'
                    }
                  />
                </TooltipContent>
              </Tooltip>
              <FormattedMessage
                id="codeBlock.highlights"
                defaultMessage={'Highlights:'}
              />
            </span>
          </li>
          <li className="flex gap-1">
            <ColoredCircle
              quantity={failCount}
              backgroundClassName="bg-lightRed"
            />
            <FormattedMessage id="global.fails" defaultMessage={'Fails'} />
          </li>
          <li className="flex gap-1">
            <ColoredCircle
              quantity={errorCount}
              backgroundClassName="bg-orange-200"
            />
            <FormattedMessage id="global.errors" defaultMessage={'Errors'} />
          </li>
          <li className="flex gap-1">
            <ColoredCircle
              quantity={highlightCount - failCount - errorCount}
              backgroundClassName="bg-mediumGray"
            />
            <FormattedMessage id="global.others" defaultMessage={'Others'} />
          </li>
        </ul>
      ) : null}
    </div>
  );
};

export default CodeBlock;
