type FeatureFlags = {
  showDev: boolean;
};

export const useFeatureFlag = (): FeatureFlags => {
  return {
    showDev: import.meta.env.VITE_FEATURE_FLAG_SHOW_DEV ?? false,
  };
};
