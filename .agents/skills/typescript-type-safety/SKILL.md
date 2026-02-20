---
name: typescript-type-safety
description: Ensures type-safe TypeScript code practices by preferring Zod validation or type guards over type assertions in TypeScript/JavaScript codebases
license: MIT
allowed-tools:
  - read
  - write
  - edit
  - bash
metadata:
  version: "1.0"
  author: "KernelCI Dashboard Team"
  tags: ["typescript", "type-safety", "validation"]
---

# TypeScript Type Safety Skill

This skill ensures type-safe TypeScript code practices by enforcing the use of runtime validation (Zod) or type guards instead of type assertions.

## Core Principles

### ❌ Avoid Type Assertions

Type assertions bypass TypeScript's type system and provide no runtime safety:

```typescript
// ❌ BAD - No runtime validation
const user = unknownData as User;
const id = obj.meta?.id as string | undefined;
```

### ✅ Prefer Zod Validation

Zod provides runtime validation and automatic TypeScript type inference:

```typescript
// ✅ GOOD - Runtime validation with Zod
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  age: z.number().optional(),
});

const result = UserSchema.safeParse(unknownData);
if (result.success) {
  const user = result.data; // Type-safe
  // use user...
} else {
  // Handle validation error
  console.error(result.error);
}
```

### ✅ Alternative: Type Guards

When Zod is not suitable, use type guard functions:

```typescript
// ✅ GOOD - Type guard with runtime check
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    typeof obj.id === 'string' &&
    'name' in obj &&
    typeof obj.name === 'string'
  );
}

if (isUser(unknownData)) {
  const user = unknownData; // Type-safe
  // use user...
}
```

## When to Use Each Approach

### Use Zod When:
- Validating external data (API responses, user input, file contents)
- Working with complex nested objects
- You need detailed error messages
- The shape of data might change over time

### Use Type Guards When:
- Simple type checks are sufficient
- Performance is critical (type guards are faster than Zod)
- Validating internal data structures
- Checking for specific object shapes

### Type Assertions Are Acceptable Only When:
- Working with DOM APIs where the type is guaranteed (e.g., `event.target as HTMLInputElement`)
- Third-party library types that are provably correct
- As a last resort with clear documentation explaining why it's safe

## Real-World Example from Codebase

From `src/components/Table/TableComponents.tsx`:

```typescript
// Define schema for column metadata
const ColumnMetaSchema = z.object({
  dataTestId: z.string().optional(),
});

// Validate at runtime
const metaResult = ColumnMetaSchema.safeParse(cell.column.columnDef.meta);
const dataTestId = metaResult.success ? metaResult.data.dataTestId : undefined;

// Use the validated data
<TableCellWithLink dataTestId={dataTestId}>
  {content}
</TableCellWithLink>
```

## Instructions for AI Agents

When you encounter code that needs type safety:

1. **Identify the source of uncertainty**: Is the data from an external source, user input, or internal code?

2. **Choose the appropriate approach**:
   - For external/untrusted data → Use Zod
   - For simple internal checks → Use type guards
   - Never use type assertions unless absolutely necessary

3. **Implement Zod validation**:
   ```typescript
   import { z } from 'zod';
   
   // Define schema
   const Schema = z.object({
     // ... your schema
   });
   
   // Validate
   const result = Schema.safeParse(data);
   if (result.success) {
     // Use result.data
   } else {
     // Handle error
   }
   ```

4. **Or implement a type guard**:
   ```typescript
   function isType(obj: unknown): obj is Type {
     return (
       typeof obj === 'object' &&
       obj !== null &&
       // ... your checks
     );
   }
   ```

5. **Test the implementation**: Ensure your validation handles edge cases and provides helpful error messages

## Benefits

- **Runtime Safety**: Catch type mismatches before they cause bugs
- **Better Error Messages**: Zod provides detailed validation errors
- **Self-Documenting**: Schemas serve as documentation
- **Refactoring Safety**: Changes to types are caught by validation
- **Production Confidence**: Validate data at boundaries (API, user input)

## References

- Zod Documentation: https://zod.dev
- TypeScript Type Guards: https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates
- Example Implementation: `src/components/Table/TableComponents.tsx`
