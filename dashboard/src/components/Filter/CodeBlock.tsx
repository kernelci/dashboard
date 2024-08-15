type TCodeBlockProps = {
  code: string;
};

const CodeBlock = ({ code }: TCodeBlockProps): JSX.Element => {
  return (
    <pre className="max-h-[275px] w-full max-w-[calc(100vw_-_398px)] overflow-x-auto bg-[#DDDDDD] p-4 font-mono text-[#767676]">
      {code}
    </pre>
  );
};

export default CodeBlock;
