# Tree Details E2E Tests - Work in Progress

## Summary

Implemented e2e tests for the tree details page (Issue #1664) using Playwright.

## What Was Done

### 1. Created Test Files
- `/home/wilsonneto/www/kernelci/dashboard/e2e/tree-details.spec.ts` - Main test file with 10 test cases
- Updated `/home/wilsonneto/www/kernelci/dashboard/e2e/e2e-selectors.ts` - Added tree details selectors

### 2. Test Cases Implemented

All 10 tests cover the requirements from issue #1664:

1. **Enter on treeListing and select a tree** ✅ PASSING
   - Navigate to `/tree`
   - Click first tree link
   - Verify URL matches `/tree/{treeName}/{branch}/{hash}` pattern

2. **Goes back one commit on commit graph** ❌ FAILING
   - Verify breadcrumb is visible
   - Verify build history graph is visible
   - URL should match `/tree/{tree}/{branch}/{hash}`

3. **Adds a filter with the card and clear all filters** ❌ FAILING
   - Click Filters button
   - Select Build Status filter
   - Verify filter selection

4. **Clicks on details button on build table and goes back via breadcrumb** ❌ FAILING
   - Navigate to tree details
   - Click details button in build table
   - Verify navigation to `/build/`
   - Click breadcrumb "Trees"
   - Verify navigation back to `/tree`

5. **Clicks on an issue details button on issue card and goes back via breadcrumb** ✅ PASSING
   - Navigate to tree details
   - Find issue card (conditional if issues exist)
   - Click issue details button
   - Verify navigation to `/issues/`
   - Click breadcrumb "Trees"
   - Verify navigation back to `/tree`

6. **Selects other tabs** ✅ PASSING
   - Click Boots tab - verify it's active
   - Click Tests tab - verify it's active
   - Click Builds tab - verify it's active

7. **Clicks on a test item and clicks on detail button for the test item** ❌ FAILING
   - Navigate to tree details
   - Click Tests tab
   - Click on a test item
   - Click details button
   - Verify navigation to `/test/`
   - Click breadcrumb "Trees"
   - Verify navigation back to `/tree`

8. **Full workflow: navigate to tree details and back via breadcrumb** ✅ PASSING
   - Navigate to `/tree`
   - Select a tree
   - Click breadcrumb "Trees"
   - Verify navigation back to `/tree`

9. **Build table status filters work correctly** ✅ PASSING
   - Verify All, Success, Failed, Inconclusive filters are visible
   - Click Success filter
   - Click All filter

10. **Search input is visible and functional** ✅ PASSING
    - Verify search input is visible
    - Type "defconfig"
    - Verify input has value

### Current Test Results

- **Passing: 6/10 tests**
- **Failing: 4/10 tests**

### Failing Tests Analysis

#### Test 2: "goes back one commit on commit graph"
- **Issue**: Selector `img[alt="Builds History"]` not finding element
- **Root Cause**: The `alt` attribute on the graph image might be different or the image has no alt text
- **Solution Needed**: Investigate actual DOM structure or use a different selector

#### Test 3: "adds a filter with card and clear all filters"
- **Issue**: Selector `.border-dark-gray:has-text("Build status")` matches multiple elements (strict mode violation)
- **Root Cause**: There are 4 "Build status" elements on the page (2 in status cards, 2 in table filters)
- **Solution Needed**: Need more specific selector or use `.first()` / `.nth()`

#### Test 4: "clicks on details button on build table and goes back via breadcrumb"
- **Issue**: Selector `a[href^="/build/"]` timing out / not finding element
- **Root Cause**: Build table might still be loading or element structure different than expected
- **Solution Needed**: Increase wait time or check actual table structure

#### Test 7: "clicks on a test item and clicks on detail button for the test item"
- **Issue**: Same as Test 4 - selector timeout
- **Root Cause**: Tests table loading or element structure different
- **Solution Needed**: Same as Test 4

### Environment Used

Tests configured to run against staging environment:
- **Base URL**: `https://staging.dashboard.kernelci.org:9000`
- **No Authentication Required**: Staging environment is open
- **Playwright Version**: 1.57.0
- **Timeout**: 30 seconds per test

### Next Steps

1. **Fix Selector Issues**: Investigate and update failing selectors based on actual DOM structure
2. **Add data-test-id Attributes**: Plan in place to add `data-test-id` attributes to React components for more reliable selectors
3. **Set Up Local Backend with Test Data**:
   - Backend has `seed_test_data.py` command to create realistic test data
   - Known test IDs available: `test123`, `issue123`, `build123`, `checkout123`, etc.
   - Plan to run backend in tmux session "zai" pane with test database
4. **Update Tests**: After selectors are fixed with `data-test-id`, update e2e tests to use them
5. **Run Against Local Backend**: Verify tests pass with local test data before running against staging

### Files Modified/Created

```
dashboard/e2e/tree-details.spec.ts           # Created - 10 test cases
dashboard/e2e/e2e-selectors.ts            # Modified - Added TREE_DETAILS_SELECTORS
```

### Test Execution Commands

```bash
# Run all tree-details tests
PLAYWRIGHT_TEST_BASE_URL=https://staging.dashboard.kernelci.org:9000 \
  pnpm exec playwright test tree-details --workers=1 --timeout=30000 --reporter=list

# Run a single test
PLAYWRIGHT_TEST_BASE_URL=https://staging.dashboard.kernelci.org:9000 \
  pnpm exec playwright test tree-details -g "enter on treeListing" --workers=1

# Run tests with headed mode (for debugging)
PLAYWRIGHT_TEST_BASE_URL=https://staging.dashboard.kernelci.org:9000 \
  pnpm exec playwright test tree-details --workers=1 --headed
```

### References

- Issue #1664: https://github.com/kernelci/dashboard/issues/1664
- Backend README: `/backend/README.md` - Database setup and test data seeding
- Seed test data command: `poetry run python3 manage.py seed_test_data`
- Test fixtures: `/backend/kernelCI_app/tests/unitTests/helpers/fixtures/`

---

**Status**: 6/10 tests passing, 4 tests failing due to selector issues

**Next Review**: Friday - Continue fixing failing selectors and setting up local backend
