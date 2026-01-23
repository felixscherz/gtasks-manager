# Feature Specification: Improve TUI UX

**Feature Branch**: `[005-improve-tui-ux]`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "I want to work on a new feature regarding improving the UX of the application. I want to work on these things:
- running `gtasks` without any commands should open the TUI
- `gtasks gui` should still work as before
- when selecting a task to toggle its state, the selection jumps back to the top but it should stay on the selected item
- the list name should be included at the top so users know which list they are editing"

## User Scenarios & Testing

### User Story 1 - Default to TUI on No Command (Priority: P1)

When a user runs `gtasks` without any subcommand or arguments, the application should automatically open the Textual User Interface (TUI) to provide immediate access to task management. This eliminates the need to remember the specific `tui` or `gui` subcommand and provides the most intuitive entry point for the application.

**Why this priority**: This is the most impactful UX improvement as it affects every user's initial interaction with the application. It removes friction and makes the application feel more responsive and user-friendly.

**Independent Test**: Can be tested by running `gtasks` with no arguments and verifying that the TUI opens successfully without any error messages. The TUI should display tasks and be fully interactive.

**Acceptance Scenarios**:

1. **Given** the application is installed and authenticated, **When** a user runs `gtasks` without any subcommand or arguments, **Then** the TUI should open and display the task list
2. **Given** the user has no saved credentials, **When** a user runs `gtasks` without any subcommand, **Then** the application should guide them through authentication before opening the TUI
3. **Given** the application is running, **When** a user runs `gtasks` with invalid arguments, **Then** the application should display help/error message instead of opening the TUI

---

### User Story 2 - Maintain Backward Compatibility (Priority: P1)

The existing `gtasks gui` command must continue to work as before. Users who have developed muscle memory for this command should experience no breaking changes. The command should open the TUI exactly as it does currently.

**Why this priority**: Maintaining backward compatibility is critical to avoid breaking existing workflows and muscle memory for current users. This ensures a smooth transition and prevents frustration.

**Independent Test**: Can be tested by running `gtasks gui` and verifying that the TUI opens with the same behavior as before (same layout, same functionality, no error messages).

**Acceptance Scenarios**:

1. **Given** the application is installed and authenticated, **When** a user runs `gtasks gui`, **Then** the TUI should open and display the task list
2. **Given** the user is in the TUI opened via `gtasks gui`, **When** they interact with any feature, **Then** all features should work identically to previous versions
3. **Given** both `gtasks` and `gtasks gui` exist as commands, **When** a user runs either command, **Then** both should result in the same TUI experience

---

### User Story 3 - Preserve Task Selection on Toggle (Priority: P2)

When a user selects a task and toggles its completion state (marking it complete or incomplete), the selection indicator should remain on that task instead of jumping back to the top of the list. This allows users to continue working on the same task list position without losing context.

**Why this priority**: This improves workflow efficiency by preventing users from having to navigate back to their previous position in the list. It's a quality-of-life improvement that reduces frustration and improves productivity.

**Independent Test**: Can be tested by selecting a task in the middle of the list, toggling its state, and verifying that the selection remains on the same task after the toggle completes.

**Acceptance Scenarios**:

1. **Given** the TUI is open with multiple tasks, **When** a user selects a task and toggles its completion state, **Then** the selection should remain on the same task after the toggle
2. **Given** the TUI is open with tasks sorted by various criteria, **When** a user toggles a task's state, **Then** the task's position may change due to sorting, but selection should follow the task to its new position
3. **Given** a user is navigating with keyboard shortcuts, **When** they toggle a task state, **Then** they should be able to continue navigation from the same task without re-positioning

---

### User Story 4 - Display List Name in Header (Priority: P2)

The TUI should display the name of the current task list in the header area so users know which list they are viewing and editing. This is especially important for users with multiple task lists who may switch between them frequently.

**Why this priority**: This improves clarity and prevents confusion when working with multiple task lists. It helps users understand the context of their current view and reduces errors from editing the wrong list.

**Independent Test**: Can be tested by opening the TUI and verifying that the list name is prominently displayed in the header area, and by switching lists to verify that the name updates accordingly.

**Acceptance Scenarios**:

1. **Given** the TUI is open, **When** a user views the task list, **Then** the current task list name should be displayed in the header
2. **Given** a user switches to a different task list, **When** the TUI refreshes, **Then** the header should display the new task list name
3. **Given** the task list name is very long, **When** it is displayed in the header, **Then** it should be truncated or abbreviated as needed to fit within the display area without breaking the layout
4. **Given** no task list is available (edge case), **When** the TUI opens, **Then** the header should display a default message like "No List Selected" or "Default List"

---

### Edge Cases

- What happens when the application is run without arguments but there are no tasks in the default list?
- How does the system handle very long task list names that exceed the display width?
- What happens if the task list metadata (name) is not available from the API?
- How does the selection preservation work when toggling the last task in the list?
- What happens if the API call to fetch list name fails while the TUI is running?
- How does the system handle the case where the task being toggled changes position in the sorted view after state change?

## Requirements

### Functional Requirements

- **FR-001**: System MUST automatically launch the TUI when `gtasks` is executed without any subcommand or arguments
- **FR-002**: System MUST maintain full backward compatibility for the `gtasks gui` command without breaking existing functionality
- **FR-003**: System MUST preserve selection on the same task after toggling its completion state
- **FR-004**: System MUST follow the task selection to its new position if the task moves due to sorting after state change
- **FR-005**: System MUST display the current task list name in the TUI header area
- **FR-006**: System MUST update the displayed list name when the user switches to a different task list
- **FR-007**: System MUST handle very long task list names by truncating or abbreviating them to fit within the display area
- **FR-008**: System MUST display a default label (e.g., "Default List" or "No List Selected") when list name is unavailable
- **FR-009**: System MUST continue to show help or error messages when `gtasks` is run with invalid arguments instead of opening the TUI
- **FR-010**: System MUST handle API errors gracefully when fetching task list metadata without crashing the TUI

### Key Entities

- **Task Selection State**: Represents the currently selected task in the TUI, including the ability to maintain this selection across UI state changes
- **Task List Metadata**: Information about the current task list being displayed, including its name and identifier, used to provide context to the user

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can launch the TUI with a single command (`gtasks`) instead of needing to remember specific subcommands
- **SC-002**: Existing users experience zero disruption when upgrading to the new version (100% backward compatibility with `gtasks gui`)
- **SC-003**: Users can toggle task completion state and continue working from the same position in the list without additional navigation (0% selection jump rate)
- **SC-004**: Users can instantly identify which task list they are viewing without needing to reference external information
- **SC-005**: Task list names are displayed in a readable format that fits within standard terminal widths (80+ characters)

### User Experience Metrics

- **SC-006**: Users report improved workflow efficiency when toggling multiple task states in succession
- **SC-007**: Users report reduced confusion when working with multiple task lists due to clear list name display
- **SC-008**: New users can access the TUI on their first attempt without reading documentation

## Assumptions

- The application has a default task list that is loaded when no specific list is requested
- The TUI framework supports dynamic header updates and selection state management
- The Google Tasks API provides task list metadata (name) in the same response as task data or through a separate API call
- Users typically work with the default task list when no specific list is specified
- Terminal display width is at least 80 characters for proper display of list names
- Task list names are reasonably short (under 50 characters) in typical use cases

## Dependencies

- None identified - this feature builds upon existing TUI functionality and API integration

## Out of Scope

- Implementing task list switching within the TUI (focus is on displaying current list name)
- Implementing custom header formatting or styling beyond displaying the list name
- Implementing persistence of selection state across TUI sessions
- Modifying other CLI commands' behavior or help text
- Adding any features beyond the four specified improvements
