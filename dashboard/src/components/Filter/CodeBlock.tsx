// import {ExcerptTests} from "./ExcerptTests";

type TCodeBlockProps = {
  code: string;
};

const CodeBlock = ({ code }: TCodeBlockProps): JSX.Element => {
  // code = ExcerptTests.excerpt1;
  let highlightCount = 0;
  code = code.replace(/</gm, '< '); // removes unwanted HTML tags
  // global multiline insensitive modifiers
  code = code.replace(
    /^.*(\berror:|([^.\n]\bfailed(\sto|\swith|\b|:|\s*[1-9]))|fail(\b|[1-9])).*$/gim,
    match => {
      highlightCount++;
      return '<span class="text-red">' + match + '</span>';
    },
  );
  return (
    <div>
      <pre className="max-h-[275px] w-full max-w-[calc(100vw_-_398px)] overflow-x-auto bg-[#DDDDDD] p-4 font-mono text-[#767676]">
        <div dangerouslySetInnerHTML={{ __html: code }}></div>
        {/* {code} */}
      </pre>
      <div>{highlightCount} Highlighted</div>
    </div>
  );
};

export default CodeBlock;
