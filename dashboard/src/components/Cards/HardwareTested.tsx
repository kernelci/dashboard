import { memo } from 'react';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import type { TTreeTestsData } from '@/types/tree/TreeDetails';

import { ScrollArea } from '@/components/ui/scroll-area';

interface IHardwareTested
  extends Pick<TTreeTestsData, 'environmentCompatible'> {
  title: IBaseCard['title'];
}

const HardwareTested = ({
  environmentCompatible,
  title,
}: IHardwareTested): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <ScrollArea className="h-[350px]">
          <DumbListingContent>
            {Object.keys(environmentCompatible).map(hardwareTestedName => {
              const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
                environmentCompatible[hardwareTestedName];

              return (
                <ListingItem
                  hasBottomBorder
                  key={hardwareTestedName}
                  text={hardwareTestedName}
                  leftIcon={
                    <GroupedTestStatus
                      done={DONE}
                      fail={FAIL}
                      error={ERROR}
                      miss={MISS}
                      pass={PASS}
                      skip={SKIP}
                      nullStatus={NULL}
                    />
                  }
                />
              );
            })}
          </DumbListingContent>
        </ScrollArea>
      }
    />
  );
};

export default memo(HardwareTested);
