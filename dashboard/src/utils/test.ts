export const isBoot = (path?: string): boolean => {
  return path !== undefined && (path === 'boot' || path.startsWith('boot.'));
};
