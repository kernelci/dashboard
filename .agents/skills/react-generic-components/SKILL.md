---
name: react-generic-components
description: Guidelines for building truly generic and reusable React components without business logic or specific use-case code in React/TypeScript codebases
license: MIT
allowed-tools:
  - read
  - write
  - edit
  - grep
metadata:
  version: "1.0"
  author: "KernelCI Dashboard Team"
  tags: ["react", "components", "architecture", "reusability"]
---

# React Generic Components Skill

This skill ensures React components remain truly generic and reusable by avoiding hardcoded business logic or use-case-specific code.

## Core Principle

**Generic components should not contain specific logic for any particular use case.**

Components should accept configuration through:
- Props
- Configuration objects
- Context (when appropriate)
- Composition patterns

## Anti-Patterns to Avoid

### ❌ Hardcoded Business Logic

```typescript
// ❌ BAD - Checking for specific values in generic component
const TableCell = ({ cell }) => {
  const dataTestId = cell.column.id === 'details' 
    ? 'details-button' 
    : undefined;
  
  return <td data-test-id={dataTestId}>...</td>;
};
```

**Problem**: This component knows about a specific column ID ("details"). It's no longer generic.

### ❌ Conditional Rendering Based on Specific Values

```typescript
// ❌ BAD - Special cases for specific data
const StatusBadge = ({ status }) => {
  if (status === 'COMPLETED') {
    return <GreenBadge>Done!</GreenBadge>;
  }
  if (status === 'FAILED') {
    return <RedBadge>Error!</RedBadge>;
  }
  return <Badge>{status}</Badge>;
};
```

**Problem**: Every new status requires modifying the component. Not scalable.

### ❌ Mixed Concerns

```typescript
// ❌ BAD - Component handles both rendering and business logic
const ChartLegend = ({ data }) => {
  // Business logic mixed in
  if (data.value === 0 && data.label !== 'important') {
    return null;
  }
  
  return <div>...</div>;
};
```

**Problem**: Generic chart component shouldn't decide what to hide based on business rules.

## Correct Patterns

### ✅ Configuration Through Props

```typescript
// ✅ GOOD - Generic, accepts configuration
interface TableCellProps {
  children: React.ReactNode;
  dataTestId?: string;
  linkProps?: LinkProps;
}

const TableCell = ({ children, dataTestId, linkProps }: TableCellProps) => {
  return (
    <td>
      <Link {...linkProps} data-test-id={dataTestId}>
        {children}
      </Link>
    </td>
  );
};
```

**Usage**:
```typescript
// Configuration happens at usage site
<TableCell 
  dataTestId="details-button"
  linkProps={detailsLink}
>
  {content}
</TableCell>
```

### ✅ Configuration Through Metadata

```typescript
// ✅ GOOD - Read configuration from metadata
const TableCell = ({ cell }) => {
  // Generic: reads from column's configuration
  const metaResult = ColumnMetaSchema.safeParse(cell.column.columnDef.meta);
  const dataTestId = metaResult.success ? metaResult.data.dataTestId : undefined;
  
  return <td data-test-id={dataTestId}>...</td>;
};
```

**Configuration** (separate from component):
```typescript
// Column definition includes metadata
const columns = [
  {
    id: 'details',
    header: () => <DetailsHeader />,
    cell: () => <DetailsIcon />,
    meta: {
      dataTestId: 'details-button', // ← Configuration
    },
  },
];
```

### ✅ Mapping Objects for Status/Variants

```typescript
// ✅ GOOD - Configuration-driven
interface StatusBadgeProps {
  status: string;
  colorMap: Record<string, string>;
  labelMap?: Record<string, string>;
}

const StatusBadge = ({ status, colorMap, labelMap }: StatusBadgeProps) => {
  const color = colorMap[status] || 'gray';
  const label = labelMap?.[status] || status;
  
  return <Badge color={color}>{label}</Badge>;
};
```

**Usage**:
```typescript
const STATUS_COLORS = {
  COMPLETED: 'green',
  FAILED: 'red',
  PENDING: 'yellow',
};

<StatusBadge status={item.status} colorMap={STATUS_COLORS} />
```

### ✅ Generic with Label-Based IDs

```typescript
// ✅ GOOD - Uses generic property from data
const ChartLegend = ({ chartValues, onClick }) => {
  return chartValues.map(value => (
    <button
      key={value.color}
      onClick={() => onClick?.(value.label)}
      data-test-id={value.label} // Generic: uses existing property
    >
      <ColorCircle color={value.color} />
      <span>{value.value}</span>
      <span>{value.label}</span>
    </button>
  ));
};
```

## Real-World Example from Codebase

### Before (Specific Logic in Generic Component)

```typescript
// ❌ BAD
const TableCellComponent = ({ cell }) => {
  const dataTestId = 
    cell.column.id === DETAILS_COLUMN_ID ? 'details-button' : undefined;
  
  return <TableCellWithLink dataTestId={dataTestId}>...</TableCellWithLink>;
};
```

### After (Generic Configuration-Based)

```typescript
// ✅ GOOD - Generic component
const ColumnMetaSchema = z.object({
  dataTestId: z.string().optional(),
});

const TableCellComponent = ({ cell }) => {
  const metaResult = ColumnMetaSchema.safeParse(cell.column.columnDef.meta);
  const dataTestId = metaResult.success ? metaResult.data.dataTestId : undefined;
  
  return <TableCellWithLink dataTestId={dataTestId}>...</TableCellWithLink>;
};

// Configuration (separate from component)
const buildColumns = [
  {
    id: DETAILS_COLUMN_ID,
    header: () => <DetailsHeader />,
    cell: () => <DetailsIcon />,
    meta: { dataTestId: 'details-button' },
  },
];
```

## Decision Tree for AI Agents

When adding functionality to a component:

```
Is this component used in multiple places?
├─ Yes → Make it generic
│   └─ Can the behavior be configured?
│       ├─ Yes → Use props/metadata
│       └─ No → Consider composition or separate components
└─ No → Specific logic may be acceptable
```

## Instructions for AI Agents

1. **Before modifying a component**:
   - Check if it's used in multiple places (`grep` or search)
   - Look for patterns like "Generic", "Reusable", or "Common" in file paths
   - Check if it's in a `components/ui/` or similar directory

2. **If the component is generic**:
   - Do NOT add hardcoded checks for specific values
   - Do NOT add business logic
   - Instead, add a prop or use configuration

3. **Choose the right approach**:
   - Simple cases → Add a prop
   - Complex cases → Use metadata/configuration objects
   - When you need the existing data property → Use that (like `label`, `id`, etc.)

4. **Verify your solution**:
   - Can this component work for ANY use case, not just the current one?
   - Is the configuration separate from the component?
   - Would adding a new variant require changing the component?
     - If yes → Refactor to be more generic

## Benefits

- **Reusability**: One component, infinite use cases
- **Maintainability**: Changes happen in configuration, not component code
- **Testability**: Generic components are easier to test
- **Scalability**: New features don't require component changes
- **Type Safety**: Configuration can be validated with Zod

## References

- Real implementation: `src/components/Table/TableComponents.tsx`
- Configuration examples: `src/components/BuildsTable/DefaultBuildsColumns.tsx`
- Related skill: `type-safety` (for validating configuration)
