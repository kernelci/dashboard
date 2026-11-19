import ReactJsonView from '@microlink/react-json-view';

import CopyButton from '@/components/Button/CopyButton';

import type { ISection } from './Section';

export const getMiscSection = ({
  misc,
  title,
}: {
  misc?: object;
  title: string;
}): ISection | undefined => {
  if (!misc || Object.keys(misc).length === 0) {
    return;
  }

  return {
    title: title,
    subsections: [
      {
        infos: [
          {
            children: (
              <div className="flex items-start gap-1">
                <ReactJsonView
                  src={misc}
                  name={false}
                  collapsed={1}
                  displayDataTypes={false}
                  style={{ fontSize: 12 }}
                />
                <CopyButton value={JSON.stringify(misc)} />
              </div>
            ),
          },
        ],
      },
    ],
  };
};
