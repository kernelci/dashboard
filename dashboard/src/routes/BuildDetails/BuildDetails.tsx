import { ImTree } from 'react-icons/im';

import { MdClose } from 'react-icons/md';

import { ISection } from '@/components/Section/Section';
import SectionGroup from '@/components/Section/SectionGroup';

const BuildDetails = (): JSX.Element => {
  return <SectionGroup sections={mockedData} />;
};

const mockedData: ISection[] = [
  {
    title: 'next-20240510',
    eyebrow: 'Build Details',
    subsections: [
      {
        infos: [
          {
            title: 'Tree',
            linkText: 'next',
            icon: <ImTree className="text-lightBlue" />,
          },
          {
            title: 'Git Branch',
            linkText: 'master',
            icon: <ImTree className="text-lightBlue" />,
          },
          {
            title: 'Git Describe',
            linkText: 'next-20240510',
          },
          {
            title: 'Defconfig',
            linkText: 'decstation_64_defconfig',
          },
          {
            title: 'Architecture',
            linkText: 'arm64',
          },
          {
            title: 'Build time',
            linkText: '108 sec',
          },
          {
            title: 'Git URL',
            linkText:
              'https://linux.kernelci.org/build/id/6683c5ecce30ba42d47e70a4/',
          },
          {
            title: 'Git commit',
            linkText: '82e4255305c554b0bb18b7ccf2db86041b4c8b6e',
          },
          {
            title: 'Date',
            linkText: '2024-07-02 09:18:36 UTC',
          },
          {
            title: 'Status',
            icon: <MdClose className="text-red" />,
          },
          {
            title: 'Build Errors',
            linkText: '3',
          },
          {
            title: 'Build warnings',
            linkText: '28',
          },
        ],
      },
      {
        infos: [
          {
            title: 'Date',
            linkText: '2024-07-02 09:18:36 UTC',
          },
          {
            title: 'Status',
            icon: <MdClose className="text-red" />,
          },
          {
            title: 'Build Errors',
            linkText: '3',
          },
          {
            title: 'Build warnings',
            linkText: '28',
          },
        ],
      },
    ],
  },
  {
    title: 'Build Platform',
    subsections: [
      {
        infos: [
          {
            title: 'System',
            linkText: 'linux',
          },
          {
            title: 'Machine type',
            linkText: 'x86_64',
          },
          {
            title: 'Node name',
            linkText: 'build-j252325-sparc-gcc-10-tinyconfig-8dtb5',
          },
          {
            title: 'CPU',
            linkText: 'AMD EPYC 7B12',
          },
        ],
      },
    ],
  },
];

export default BuildDetails;
