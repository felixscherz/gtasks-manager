# Feature Specification: VIM Keybindings for TUI Task List

**Feature Branch**: `003-vim-keybindings`
**Created**: 2025-01-11
**Status**: Draft
**Input**: User description: "I want to refine the TUI interface as it is currently clunky and does not seem to be working properly. The initial view when opening the applicaiont is a list view where only arrow keys work to navigate. I want this initial list view to support VIM navigation (j,k to move down/up) and also suppoert ENTER to toggle the todo state."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - VIM Navigation (Priority: P1)

As a user familiar with VIM-style navigation, I want to move up and down through the task list using 'j' and 'k' keys instead of arrow keys, so that I can navigate efficiently using keyboard shortcuts I'm already accustomed to.

**Why this priority**: This is the primary user request and core feature that improves the TUI navigation experience for VIM users. Without this, the TUI remains clunky for a significant user demographic.

**Independent Test**: Can be fully tested by opening the TUI and pressing 'j' and 'k' to verify list selection moves up and down, without any other features being implemented.

**Acceptance Scenarios**:

1. **Given** the TUI task list is displayed with multiple tasks, **When** the user presses 'j', **Then** the selection moves to the next task in the list (moves down one item)
2. **Given** the TUI task list is displayed with multiple tasks, **When** the user presses 'k', **Then** the selection moves to the previous task in the list (moves up one item)
3. **Given** the selection is at the top of the task list, **When** the user presses 'k', **Then** the selection remains at the top task (no movement beyond boundaries)
4. **Given** the selection is at the bottom of the task list, **When** the user presses 'j', **Then** the selection remains at the bottom task (no movement beyond boundaries)

---

### User Story 2 - Toggle Task with ENTER (Priority: P1)

As a user managing tasks, I want to press ENTER on the currently selected task to toggle its completion state (todo ↔ completed), so that I can quickly mark tasks as done or undone without navigating through menus or using other keyboard shortcuts.

**Why this priority**: This is explicitly requested by the user and provides the core task management interaction in the TUI. Without this, users must use alternative methods to change task status, which is inefficient.

**Independent Test**: Can be fully tested by opening the TUI, selecting a task, and pressing ENTER to verify the task's completion state toggles between done and undone.

**Acceptance Scenarios**:

1. **Given** a task is selected and its status is "needsAction" (not completed), **When** the user presses ENTER, **Then** the task's status changes to "completed" and the task visually indicates it's done
2. **Given** a task is selected and its status is "completed", **When** the user presses ENTER, **Then** the task's status changes to "needsAction" and the task visually indicates it's not done
3. **Given** no task is selected, **When** the user presses ENTER, **Then** nothing happens or an appropriate visual feedback is provided
4. **Given** a task is selected, **When** the user presses ENTER multiple times rapidly, **Then** the task's status toggles back and forth with each press (debouncing not required)

---

### User Story 3 - Arrow Keys Continue Working (Priority: P2)

As a user who is not familiar with VIM keybindings or who prefers traditional navigation, I want arrow keys to continue working alongside the new 'j' and 'k' keys, so that I can navigate using whichever method is most comfortable for me.

**Why this priority**: This ensures backward compatibility and accessibility. It's important for users who don't know VIM shortcuts, but less critical than the primary VIM feature request.

**Independent Test**: Can be tested by verifying that arrow keys still function correctly before and after implementing VIM keybindings.

**Acceptance Scenarios**:

1. **Given** the TUI task list is displayed, **When** the user presses the down arrow key, **Then** the selection moves to the next task in the list
2. **Given** the TUI task list is displayed, **When** the user presses the up arrow key, **Then** the selection moves to the previous task in the list
3. **Given** the TUI task list is displayed, **When** the user alternates between arrow keys and 'j'/'k' keys, **Then** both methods consistently move the selection correctly

---

### User Story 4 - Visual Feedback for Selected Task (Priority: P3)

As a user navigating through tasks, I want the currently selected task to have clear visual highlighting, so that I can easily identify which task will be toggled when I press ENTER.

**Why this priority**: While important for usability, this is likely already implemented or can be inferred from standard TUI patterns. It's a nice-to-have that enhances the user experience but doesn't block core functionality.

**Independent Test**: Can be tested by verifying that navigating through the list shows clear visual indication of the selected item.

**Acceptance Scenarios**:

1. **Given** the TUI task list is displayed, **When** the selection moves to a task using 'j', 'k', or arrow keys, **Then** the task is visually highlighted to indicate it's selected
2. **Given** the TUI task list is displayed, **When** the selection moves away from a task, **Then** the visual highlighting is removed from that task
3. **Given** the TUI is in a terminal with limited color support, **When** a task is selected, **Then** there is still visible indication (e.g., inverted colors, underline, or other distinct styling)

---

### Edge Cases

- What happens when the task list is empty and user presses 'j', 'k', or ENTER? (Selection handling and feedback)
- What happens when a task is being toggled and the user navigates away before the operation completes? (Race condition handling)
- What happens if the user holds down 'j' or 'k' for continuous navigation? (Repeated key press handling)
- What happens when the user presses ENTER immediately after the TUI loads? (Default selection behavior)
- What happens if the task toggle fails due to an API error? (Error feedback and state recovery)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to navigate down through the task list by pressing the 'j' key
- **FR-002**: System MUST allow users to navigate up through the task list by pressing the 'k' key
- **FR-003**: System MUST prevent navigation beyond the top boundary when the user presses 'k' at the first task
- **FR-004**: System MUST prevent navigation beyond the bottom boundary when the user presses 'j' at the last task
- **FR-005**: System MUST allow users to toggle the completion state of the currently selected task by pressing ENTER
- **FR-006**: System MUST continue to support up arrow key navigation alongside 'k' key
- **FR-007**: System MUST continue to support down arrow key navigation alongside 'j' key
- **FR-008**: System MUST visually highlight the currently selected task in the list
- **FR-009**: System MUST provide visual feedback when a task is toggled to completed status
- **FR-010**: System MUST provide visual feedback when a task is toggled to needsAction status
- **FR-011**: System MUST handle the ENTER key gracefully when no task is selected or the task list is empty
- **FR-012**: System MUST update the task's completion status persistently after a successful ENTER toggle

### Key Entities *(include if feature involves data)*

- **Task**: Represents a todo item with attributes including unique identifier, title, completion status (needsAction or completed), and optional notes/due date
- **Task List**: Ordered collection of tasks displayed in the TUI, with a current selection state indicating which task is active
- **Selection State**: Tracks which task is currently selected in the list, enabling keyboard-driven operations like ENTER toggle

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate through a 10-item task list using only 'j' and 'k' keys within 5 seconds, reaching any task efficiently
- **SC-002**: Users can toggle 5 tasks from needsAction to completed using only the ENTER key in under 10 seconds, demonstrating efficient task state management
- **SC-003**: 100% of VIM-style navigation operations (j/k key presses) correctly move selection within list boundaries without errors
- **SC-004**: 95% of users familiar with VIM report that the TUI navigation feels natural and efficient based on user feedback surveys
- **SC-005**: Arrow keys continue to function correctly alongside VIM keys, with 0 regression in existing navigation functionality

---

## Assumptions

### Technical Assumptions

- The TUI framework (Textual) supports capturing and processing 'j', 'k', and ENTER key events
- Task selection is already implemented or can be added to track the currently active task
- The existing Google Tasks API integration supports updating task completion status
- Visual highlighting can be achieved through the TUI framework's styling capabilities

### User Experience Assumptions

- Users who request VIM keybindings are familiar with VIM's j/k navigation pattern (j = down, k = up)
- Users expect immediate visual feedback when toggling task completion status
- Standard TUI patterns for list selection and highlighting apply
- Keyboard navigation should work without requiring mouse input

### Scope Assumptions

- This feature applies only to the initial list view when opening the application
- Only navigation keys (j/k) and toggle key (ENTER) are in scope; other VIM keys (h/l, /, etc.) are not included
- No configuration or preference system for enabling/disabling VIM keybindings is required
- Task filtering, sorting, or other list manipulation features are out of scope for this feature

### Data Assumptions

- Task completion status toggles between "needsAction" and "completed" states
- Tasks persist their state to the Google Tasks API after successful toggle operations
- Empty task lists are handled gracefully without causing errors when navigation keys are pressed

## Notes

- This specification assumes the TUI framework already supports keyboard event handling. If the current framework has limitations, the implementation approach may need to adjust while maintaining the same user-facing behavior.
- The feature focuses on the initial list view as stated in the user request. If the application has other views or screens, they may or may not require similar keybindings (out of scope).
- Visual feedback for task toggling should be immediate but the persistence to the backend may be asynchronous; users should see the status change even if the API call is in progress.
