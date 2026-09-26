# PR Requirements Checklist

## ✅ ReactRootManager Class (src/utils/react.tsx)

- [x] File created at exactly `src/utils/react.tsx`
- [x] Class named `ReactRootManager`
- [x] Method: `render(children: ReactNode, element: Element): void`
  - [x] Uses `createRoot` from `react-dom/client`
  - [x] Tracks roots for later unmounting
  - [x] Uses `flushSync` for synchronous rendering
- [x] Method: `unmount(): void`
  - [x] Unmounts all managed React roots
  - [x] Clears associated container elements
- [x] Getter: `elements: Element[]`
  - [x] Returns list of DOM elements with mounted roots
  - [x] Useful for deduplication and external reference

## ✅ PersistedElement Component

- [x] Uses `createRoot` instead of `ReactDOM.render`
- [x] Stores mapping of persistent roots in static `rootMap`
- [x] `destroyElement` method calls `.unmount()` on associated Root
- [x] `isMounted` method checks for presence of root in `rootMap`
- [x] Master container ID: `"mx_PersistedElement_container"`
- [x] Element container ID format: `"mx_persistedElement_" + persistKey`

## ✅ EditHistoryMessage Component

- [x] Instantiates `ReactRootManager` objects for pills and tooltips
- [x] `componentWillUnmount` calls `unmount()` on both managers
- [x] `tooltipifyLinks` references `.elements` from ReactRootManager

## ✅ TextualBody Component

- [x] Uses `ReactRootManager.render` instead of `ReactDOM.render`
- [x] Manages code blocks, spoilers, and pills via ReactRootManager
- [x] `componentWillUnmount` calls `unmount()` on all three managers (pills, tooltips, reactRoots)
- [x] `wrapPreInReact` registers via `reactRoots.render`
- [x] Spoiler rendering uses `reactRoots.render`
- [x] `tooltipifyLinks` receives `[...pills.elements, ...reactRoots.elements]`

## ✅ pillifyLinks Function

- [x] Uses `ReactRootManager` to track and render pills
- [x] Calls `ReactRootManager.render` instead of `ReactDOM.render`
- [x] Checks `pills.elements` to prevent duplicate pillification
- [x] Supports backward compatibility with `Element[]` parameter
- [x] Legacy `unmountPills` helper removed

## ✅ tooltipifyLinks Function

- [x] Uses `ReactRootManager` to track and inject tooltips
- [x] Calls `ReactRootManager.render` instead of `ReactDOM.render`
- [x] Uses `tooltips.elements` to skip already-managed nodes
- [x] Supports backward compatibility with `Element[]` parameter
- [x] Legacy `unmountTooltips` function removed

## ✅ HtmlExport (getEventTile method)

- [x] Uses `createRoot` to render EventTile instances
- [x] Renders into temporary DOM node
- [x] Temporary root unmounted explicitly via `.unmount()`

## ✅ Special Constants and IDs

- [x] `"mx_PersistedElement_container"` - Master container ID
- [x] `"mx_persistedElement_" + persistKey` - Element container ID format
- [x] `"@room"` - Hardcoded mention string (used in existing code)
- [x] Skips nodes with: `tagName === "PRE"`, `tagName === "CODE"`
- [x] Checks: `event.getContent().format === "org.matrix.custom.html"`

## ✅ Testing

- [x] All pillify tests pass (4/4)
- [x] All tooltipify tests pass (4/4)
- [x] All TextualBody tests pass (23/23)
- [x] Backward compatibility maintained for test code
- [x] No modifications needed to test files

## ✅ Code Quality

- [x] No `ReactDOM.render` in pillify.tsx
- [x] No `ReactDOM.render` in tooltipify.tsx
- [x] No `ReactDOM.render` in TextualBody.tsx
- [x] Proper imports: `import { createRoot } from "react-dom/client"`
- [x] Proper imports: `import { flushSync } from "react-dom"`
- [x] TypeScript types properly defined
- [x] Backward compatibility for legacy APIs

## Summary

✅ **ALL REQUIREMENTS MET**

The implementation successfully:
1. Creates ReactRootManager utility class
2. Migrates all components to use createRoot
3. Removes legacy ReactDOM.render usage
4. Maintains backward compatibility
5. Passes all existing tests
6. Follows React 18 best practices
7. Properly manages lifecycle and cleanup
