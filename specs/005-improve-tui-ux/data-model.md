# Data Model

**Feature**: Improve TUI UX
**Date**: 2026-01-17
**Phase**: Phase 1 - Design Complete

## Overview

This document defines the data structures and entities used in the TUI UX improvements. The feature introduces new entities for TUI state management and extends existing task list metadata handling.

## Core Entities

### TUI Selection State

**Purpose**: Tracks the currently selected task in the TUI and preserves selection across state changes.

**Fields**:
- `task_id: str` - Unique identifier of the currently selected task (from Google Tasks API)
- `preserved: bool` - Flag indicating if selection should be preserved across updates
- `timestamp: datetime` - When the selection was last updated

**Validation Rules**:
- `task_id` must be a valid Google Tasks task ID (non-empty string)
- `timestamp` must be current or recent (within session lifetime)

**State Transitions**:
```
[No Selection] -- user navigates --> [Task Selected]
[Task Selected] -- user toggles state --> [Selection Preserved]
[Selection Preserved] -- list refreshes --> [Selection Restored]
[Task Selected] -- user navigates away --> [No Selection]
```

**Use Cases**:
- User selects task in list
- User toggles task completion state
- TUI refreshes task list (may cause re-sorting)
- User continues navigation from same task

**Relationships**:
- References `Task` entity via `task_id`

---

### Task List Metadata

**Purpose**: Stores information about the current task list being displayed in the TUI.

**Fields**:
- `list_id: str` - Unique identifier of the task list (from Google Tasks API)
- `name: str` - Human-readable name of the task list
- `fetched_at: datetime` - When the metadata was last fetched from API
- `is_cached: bool` - Flag indicating if metadata is from cache or fresh API call

**Validation Rules**:
- `list_id` must be a valid Google Tasks task list ID (non-empty string)
- `name` must be non-empty string, max 255 characters (Google API constraint)
- `fetched_at` must be a valid datetime
- `is_cached` is boolean

**State Transitions**:
```
[Unknown List] -- fetch from API --> [Fresh Metadata]
[Fresh Metadata] -- cache expires --> [Stale Metadata]
[Stale Metadata] -- refresh from API --> [Fresh Metadata]
```

**Use Cases**:
- Display list name in TUI header
- Switch between task lists
- Handle API failures gracefully (use cached metadata or default)

**Relationships**:
- One-to-many with `Task` entities (a list contains multiple tasks)

---

### TUI Application State

**Purpose**: Manages overall TUI application state including selection, list metadata, and UI mode.

**Fields**:
- `selection: TUISelectionState` - Current task selection
- `current_list: TaskListMetadata` - Current task list being displayed
- `is_loading: bool` - Flag indicating if async operation is in progress
- `error_message: Optional[str]` - Current error message to display, if any

**Validation Rules**:
- `selection` may be null (no task selected)
- `current_list` must always be present (even if cached or default)
- `is_loading` is boolean
- `error_message` may be null (no error) or non-empty string

**State Transitions**:
```
[Idle] -- user interaction --> [Loading]
[Loading] -- API success --> [Idle]
[Loading] -- API error --> [Error State]
[Error State] -- user dismisses --> [Idle]
```

**Use Cases**:
- TUI initialization
- Task state toggling (with loading indicator)
- List refresh operations
- Error handling and user feedback

**Relationships**:
- Composed of `TUISelectionState` and `TaskListMetadata`

---

## Extended Entities

### Task (Existing, Extended Context)

**Existing Fields** (from Google Tasks API):
- `id: str` - Unique identifier
- `title: str` - Task title
- `notes: Optional[str]` - Task notes
- `status: str` - "needsAction" or "completed"
- `due: Optional[str]` - Due date in ISO 8601 format
- `completed: Optional[str]` - Completion timestamp

**New Context**:
- Task is reference target for `TUISelectionState.task_id`
- Task position in list may change after state toggling (due to sorting)
- Task belongs to a specific `TaskListMetadata.list_id`

---

## Data Flow

### Task Selection Preservation Flow

```
1. User selects task (task_id = "abc123")
   → TUISelectionState.task_id = "abc123"
   → TUISelectionState.timestamp = now

2. User toggles task state (mark complete)
   → is_loading = true
   → API call in background worker

3. API completes, list refreshes (tasks may re-sort)
   → Task "abc123" moves from index 5 to index 12

4. Selection restoration
   → Find task with id "abc123" in refreshed list
   → Move highlight to index 12
   → is_loading = false
```

### List Name Display Flow

```
1. TUI initialization
   → Fetch TaskListMetadata from API (list_id, name)
   → Display name in header widget

2. List name updates (if user switches lists)
   → Fetch new TaskListMetadata
   → Update header widget (reactive update)

3. API error handling
   → Use cached TaskListMetadata if available
   → Fallback to "Default List" if no cache
```

---

## Validation Summary

| Entity | Required Fields | Type Constraints | Business Rules |
|--------|----------------|------------------|----------------|
| TUISelectionState | task_id | Non-empty string, datetime | Task ID must exist in current list |
| TaskListMetadata | list_id, name | Non-empty strings, datetime | Name max 255 chars, fallback to default |
| TUIApplicationState | current_list | Boolean, optional string | Always has current_list, error clearable |

---

## Implementation Notes

### Storage Strategy
- `TUISelectionState`: In-memory only (not persisted)
- `TaskListMetadata`: Cached in memory during TUI session
- `TUIApplicationState`: In-memory only

### Performance Considerations
- Selection preservation requires O(n) scan for task ID after list refresh
- Task list metadata fetched once per TUI session (not per refresh)
- Cache metadata for 5 minutes to balance freshness vs performance

### Error Handling
- Missing task ID during selection restoration → Clear selection
- Failed task list metadata fetch → Use cached or default name
- Multiple errors in session → Display latest error only

### Testing Considerations
- Unit tests for state transitions
- Integration tests for selection preservation across state changes
- Error case tests (API failures, missing metadata)
- Performance tests for large task lists (100+ tasks)
