# Feature Specification: Add VIM keybindings

**Feature Branch**: `002-add-vim-keybindings`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Key bindings should follow VIM conventions: hjkl to move left, down, up, right respectively, enter to toggle the tasks as done / not done."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate task list with VIM keys (Priority: P1)

As a keyboard-focused user, I want to use `h`, `j`, `k`, `l` to move through the TUI so I can navigate tasks quickly without reaching for the mouse.

**Why this priority**: Enables efficient keyboard-driven navigation, core to TUI usability and accessibility for power users.

**Independent Test**: With the TUI open and a list of tasks visible, pressing `j` moves selection down one item, `k` moves up, `h` moves focus left (e.g., to a sidebar or previous column), and `l` moves focus right. Each key press results in immediate visual change indicating the new selection.

**Acceptance Scenarios**:

1. **Given** a list with multiple tasks visible, **When** the user presses `j`, **Then** the selection moves to the next task and UI highlights it.
2. **Given** a list with multiple tasks visible, **When** the user presses `k`, **Then** the selection moves to the previous task and UI highlights it.
3. **Given** the UI has multiple panes (e.g., sidebar and task list), **When** the user presses `h`, **Then** focus moves to the left pane.
4. **Given** the UI has multiple panes, **When** the user presses `l`, **Then** focus moves to the right pane.

---

### User Story 2 - Toggle task completion with Enter (Priority: P1)

As a user managing tasks via keyboard, I want pressing `Enter` on the selected task to toggle its completion state so I can quickly mark tasks done or undone.

**Why this priority**: Toggling completion is a core action in task management; mapping it to `Enter` aligns with user expectations and accelerates workflows.

**Independent Test**: With a task selected, pressing `Enter` changes its visual state (e.g., checkmark or strike-through) and updates the underlying status to `completed` or `needsAction`.

**Acceptance Scenarios**:

1. **Given** a selected pending task, **When** the user presses `Enter`, **Then** the task becomes completed and displays as such.
2. **Given** a selected completed task, **When** the user presses `Enter`, **Then** the task becomes pending and displays as such.
3. **Given** the network/API is unavailable, **When** the user presses `Enter`, **Then** the UI shows an error notification and reverts the visual change if persistence fails. (Behavior: optimistic UI update with background persistence and rollback on failure — see `specs/002-add-vim-keybindings/research.md`.)

---

### User Story 3 - Respect existing shortcuts and accessibility (Priority: P2)

As a user, I want VIM bindings to coexist with existing shortcuts and not break accessibility tools so that users retain discoverability and alternative input methods still work.

**Why this priority**: Prevents regressions for users relying on existing shortcuts or assistive tech.

**Independent Test**: Existing non-VIM keyboard shortcuts continue to work; screen readers can still navigate focusable elements.

**Acceptance Scenarios**:

1. **Given** an existing shortcut (e.g., `c` for create), **When** VIM mode is enabled, **Then** that shortcut remains available unless explicitly overridden.
2. **Given** a screen reader in use, **When** VIM keys are pressed, **Then** focus changes are announced appropriately.

---

### Edge Cases

- What happens when the user types `j` while focused on a text input (should not trigger navigation)?
- How to handle rapid key repeats (holding `j` to scroll)?
- How to signal mode (if there is a separate VIM mode toggle) to the user?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The TUI MUST map `j` to move selection down one item in the currently focused list or pane.
- **FR-002**: The TUI MUST map `k` to move selection up one item in the currently focused list or pane.
- **FR-003**: The TUI MUST map `h` to move focus to the left pane/column when applicable.
- **FR-004**: The TUI MUST map `l` to move focus to the right pane/column when applicable.
- **FR-005**: The TUI MUST map `Enter` to toggle the selected task's completion state between `completed` and `needsAction`.
- **FR-006**: Key bindings MUST not trigger while focus is inside text input fields or when user is typing.
- **FR-007**: The system MUST provide user feedback when toggling task state, including visual change and a transient confirmation message on failure.
- **FR-008**: The implementation MUST not break existing keyboard shortcuts; conflicts MUST be documented and resolved by preference order.
- **FR-009**: Rapid key repeats (holding navigation keys) MUST result in smooth repeated navigation without UI freeze.
- **FR-010**: The feature MUST be covered by automated and manual tests that validate navigation and toggling behavior.

### Key Entities *(include if feature involves data)*

- **Task**: Represents a task object with attributes: `id`, `title`, `status` (`needsAction` or `completed`), `notes`, `due`.
- **UI Focus**: Represents the currently focused pane or element; used to determine how navigation keys operate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of keyboard users can navigate to a task and toggle its completion within 5 seconds using VIM keys in a usability test.
- **SC-002**: No keyboard shortcut regressions reported in the first QA cycle (0 known regressions).
- **SC-003**: Navigation key latency is under 100ms for UI updates in local testing environments.
- **SC-004**: Automated tests cover 90% of navigation and toggle interactions for the TUI component.

## Assumptions

- The TUI supports multiple panes (sidebar and main task list) or the mapping to left/right will be a no-op if only a single pane exists.
- There is a clear concept of focus in the UI to determine where navigation applies.
- Default behavior: VIM keybindings are enabled by default for the TUI; users can opt out later via settings. (Decision: default enabled; user-toggleable — see `specs/002-add-vim-keybindings/research.md`.)

## Notes

- This specification avoids implementation details and focuses on observable behavior and tests.
