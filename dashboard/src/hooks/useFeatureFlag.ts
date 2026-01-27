type FeatureFlags = {
  showDev: boolean;
  treeListingVersion: string;
};

export const useFeatureFlag = (): FeatureFlags => {
  return {
    showDev: import.meta.env.VITE_FEATURE_FLAG_SHOW_DEV ?? false,
    treeListingVersion:
      import.meta.env.VITE_FEATURE_FLAG_TREE_LISTING_VERSION ?? 'v1',
  };
};
