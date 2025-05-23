import { useMemo, type JSX } from 'react';

interface ISummarySectionColumn {
  title: string;
  value: string;
}

export interface ISummarySection {
  title: string;
  columns: ISummarySectionColumn[];
}

const SummarySectionColumn = ({
  title,
  value,
}: ISummarySectionColumn): JSX.Element => {
  return (
    <div>
      <h5 className="mb-1 text-sm font-medium">{title}</h5>
      <span className="text-sm font-normal">{value}</span>
    </div>
  );
};

const SummarySection = ({ title, columns }: ISummarySection): JSX.Element => {
  const columnComponents = useMemo(
    () =>
      columns.map(column => (
        <SummarySectionColumn key={column.title} {...column} />
      )),
    [columns],
  );

  return (
    <div className="text-dim-gray min-h-[100px]">
      <h4 className="mb-6 text-xl font-semibold">{title}</h4>
      <div className="flex justify-between">{columnComponents}</div>
    </div>
  );
};

export default SummarySection;
