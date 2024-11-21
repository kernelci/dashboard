import { z } from 'zod';

import type {
  ArchCompilerStatus,
  BuildsTabBuild,
  BuildStatus,
  StatusCounts,
  TestHistory,
  TIssue,
} from '@/types/general';

type BuildSummary = {
  builds: BuildStatus;
  configs: Record<string, BuildStatus>;
  architectures: Record<
    string,
    {
      valid: number;
      invalid: number;
      null: number;
      compilers: string[];
    }
  >;
};

type BuildsData = {
  items: BuildsTabBuild[];
  issues: TIssue[];
  summary: BuildSummary;
};

type Tests = {
  archSummary: ArchCompilerStatus[];
  history: TestHistory[];
  platformsFailing: string[];
  statusSummary: StatusCounts;
  failReasons: Record<string, unknown>;
  configs: Record<string, StatusCounts>;
  issues: TIssue[];
};

export type Trees = {
  treeName?: string;
  gitRepositoryBranch?: string;
  gitRepositoryUrl?: string;
  headGitCommitName?: string;
  headGitCommitHash?: string;
  index: string;
};
export type THardwareDetails = {
  builds: BuildsData;
  tests: Tests;
  boots: Tests;
  trees: Trees[];
};

// TODO: move to general types
const zFilterBoolValue = z.record(z.boolean()).optional();
const zFilterNumberValue = z.number().optional();

export const zFilterObjectsKeys = z.enum([
  'configs',
  'archs',
  'compilers',
  'buildStatus',
  'bootStatus',
  'testStatus',
  'trees',
]);
export const zFilterNumberKeys = z.enum([
  'buildDurationMin',
  'buildDurationMax',
  'bootDurationMin',
  'bootDurationMax',
  'testDurationMin',
  'testDurationMax',
]);

export type TFilterKeys =
  | z.infer<typeof zFilterObjectsKeys>
  | z.infer<typeof zFilterNumberKeys>;

export const zDiffFilter = z
  .union([
    z.object({
      configs: zFilterBoolValue,
      archs: zFilterBoolValue,
      buildStatus: zFilterBoolValue,
      compilers: zFilterBoolValue,
      bootStatus: zFilterBoolValue,
      testStatus: zFilterBoolValue,
      buildDurationMax: zFilterNumberValue,
      buildDurationMin: zFilterNumberValue,
      bootDurationMin: zFilterNumberValue,
      bootDurationMax: zFilterNumberValue,
      testDurationMin: zFilterNumberValue,
      testDurationMax: zFilterNumberValue,
      trees: zFilterBoolValue,
    } satisfies Record<TFilterKeys, unknown>),
    z.record(z.never()),
  ])
  .catch({});
