import { format } from 'date-fns';

import type { IListingItem } from '@/components/ListingItem/ListingItem';
import type { ISummaryItem } from '@/components/Summary/Summary';
import type {
  BuildsTabBuild,
  BuildStatus,
  TArch,
  AccordionItemBuilds,
} from '@/types/tree/TreeDetails';

export function formatDate(date: Date | string, short?: boolean): string {
  const options: Intl.DateTimeFormatOptions = {
    year: short ? '2-digit' : 'numeric',
    month: short ? 'numeric' : 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: short ? undefined : 'short',
  };

  if (typeof date === 'string') date = new Date(date);
  if (isNaN(date.getTime())) return '-';

  return new Intl.DateTimeFormat('en-US', options).format(date);
}

export const getDateOffset = (date: Date): string => {
  return format(date, 'z');
};

export const sanitizeArchs = (archs: TArch | undefined): ISummaryItem[] => {
  if (!archs) return [];
  return Object.entries(archs).map(([key, value]) => ({
    arch: {
      text: key,
      errors: value.invalid,
      success: value.valid,
      unknown: value.null,
    },
    compilers: value.compilers,
  }));
};

export const sanitizeConfigs = (
  configs: Record<string, BuildStatus> | undefined,
): IListingItem[] => {
  if (!configs) return [];

  return Object.entries(configs).map(([key, value]) => ({
    text: key,
    errors: value.invalid,
    success: value.valid,
    unknown: value.null,
  }));
};

const isBuildError = (build: BuildsTabBuild): number => {
  return build.valid || build.valid === null ? 0 : 1;
};

export const sanitizeBuilds = (
  builds: BuildsTabBuild[] | undefined,
): AccordionItemBuilds[] => {
  if (!builds) return [];

  return builds.map(build => ({
    id: build.id,
    config: build.config_name,
    date: build.start_time,
    buildTime: build.duration,
    compiler: build.compiler,
    buildErrors: isBuildError(build),
    status: build.valid === null ? 'null' : build.valid ? 'valid' : 'invalid',
    buildLogs: build.log_url,
    kernelConfig: build.config_url,
    kernelImage: build.misc ? build.misc['kernel_type'] : undefined,
    dtb: build.misc ? build.misc['dtb'] : undefined,
    systemMap: build.misc ? build.misc['system_map'] : undefined,
    modules: build.misc ? build.misc['modules'] : undefined,
  }));
};

export const sanitizeBuildsSummary = (
  buildsSummary: BuildStatus | undefined,
): BuildStatus =>
  buildsSummary ? buildsSummary : { invalid: 0, null: 0, valid: 0 };
