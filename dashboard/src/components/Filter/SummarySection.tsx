import { useMemo } from 'react';

interface ISummarySectionColumn {
  title: string;
  value: string;
}

export interface ISummarySection {
  title: string;
  columns: ISummarySectionColumn[];
}

const SummarySectioncolumn = ({
  title,
  value,
}: ISummarySectionColumn): JSX.Element => {
  return (
    <div>
      <h5 className="font-medium text-sm mb-1">{title}</h5>
      <span className="font-normal text-sm">{value}</span>
    </div>
  );
};

const SummarySection = ({ title, columns }: ISummarySection): JSX.Element => {
  const columnComponents = useMemo(
    () =>
      columns.map(column => (
        <SummarySectioncolumn key={column.title} {...column} />
      )),
    [columns],
  );

  return (
    <div className="min-h-[100px] text-dimGray">
      <h4 className="font-semibold text-xl mb-6">{title}</h4>
      <div className="flex justify-between ">{columnComponents}</div>
    </div>
  );
};

export default SummarySection;
