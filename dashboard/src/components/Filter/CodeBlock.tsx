import { LiaInfoCircleSolid } from 'react-icons/lia';

import { cn } from '@/lib/utils';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';

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
    /^.*((\berror(:|\s*-*[1-9]|))|([^\n]\bfailed(\sto|\swith|\b|:|\s*[1-9]))|(fail(\b|[1-9]))).*$/gim,
    match => {
      highlightCount++;
      if (match.search(/fail/i) !== -1) {
        // ignores .failed files and fail flags
        if (match.search(/(.failed|[|/]fail\b)/i) !== -1) {
          return '<span class="text-blue">' + match + '</span>';
        }
        failCount++;
        return '<span class="text-red">' + match + '</span>';
      } else {
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
        <ul className={cn('py-2 pl-3', highlightsClassname)}>
          <li>
            {/* TODO: add locale, add better description */}
            <span className="flex items-center gap-1">
              {highlightCount} Highlighted
              <Tooltip>
                <TooltipTrigger>
                  <LiaInfoCircleSolid />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Highlighted items are any lines citing fails or errors.</p>
                </TooltipContent>
              </Tooltip>
            </span>
          </li>
          <li>{failCount} Fails</li>
          <li>{errorCount} Errors</li>
        </ul>
      ) : null}
    </div>
  );
};

export default CodeBlock;
