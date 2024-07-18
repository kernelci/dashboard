import Accordion, { IAccordionItems } from '../Accordion/Accordion';

interface IBuildsTable {
  buildsData?: IAccordionItems[];
}

const BuildsTable = ({ buildsData }: IBuildsTable): JSX.Element => {
  return (
    <div>
      {buildsData && (
        <Accordion
          type="build"
          headers={[
            'Config',
            'Compiler',
            'Date',
            'Build Errors',
            'Build Time',
            'Status',
          ]}
          items={buildsData}
        />
      )}
    </div>
  );
};

export default BuildsTable;
