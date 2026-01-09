# Research: Add VIM Keybindings

Feature context: Add VIM-style navigation keys (`h`,`j`,`k`,`l`) and `Enter` toggling to the Textual TUI.

---

## Unknowns and Decisions

### 1) Offline / error behavior when toggling completion
- Decision: Optimistic UI update with background persistence and rollback on failure.
- Rationale: Provides immediate feedback and aligns with user expectation of instant toggling (spec SC-003). Textual supports dispatching background work with `@work`, allowing API calls to be performed asynchronously while the UI reflects the change immediately. On failure, show a transient error notification and revert the status to previous state.
- Alternatives considered:
  - Strict confirmation after API success (slower, feels laggy)
  - Queueing changes for offline sync (more complex, out of scope for this feature)

### 2) Default mode: enabled vs opt-in
- Decision: Enable VIM bindings by default for the TUI but provide a user setting to disable them.
- Rationale: Spec assumes default enabled (spec Assumptions). Default-on gives immediate value to keyboard users while allowing opt-out for discoverability and accessibility concerns.
- Alternatives considered:
  - Opt-in default: reduces surprise but requires onboarding/settings UI.

### 3) Error messaging and transient notification design
- Decision: Use a small transient notification area in the TUI (Textual `Notification` pattern) showing short messages (e.g., "Failed to save: network error"), with a visual revert if persistence fails.
- Rationale: Clear, minimally intrusive feedback for common failures; aligns with existing project patterns that use checkmarks and transient messages.
- Alternatives considered: modal dialogs (too disruptive).

### 4) Accessibility (screen readers and focus announcements)
- Decision: Ensure focus changes use Textual's built-in focus management APIs and emit accessibility announcements via `announce` helper (or accessible attribute if available) on focus change.
- Rationale: Textual's current accessibility story is limited; using focus APIs is the most compatible approach. We will add tests to validate focus transitions and include accessibility notes in docs.
- Alternatives considered: Integrating with external screen reader APIs (platform-dependent; deferred).

### 5) Rapid key repeats (holding navigation keys)
- Decision: Rely on terminal/OS native key repeat and handle repeat events; ensure event handling is lightweight and does not block (no debounce). If performance issues appear, consider adding rate limiting.
- Rationale: Simpler and consistent with user expectation of holding keys to move.
- Alternatives considered: Implementing custom repeat handling (complex, unnecessary initially).

### 6) Mode indicator UI
- Decision: No separate modal mode; VIM bindings active in default mode. Add a small status bar indicator "VIM" that can be toggled via settings to signal whether VIM bindings are active.
- Rationale: Minimally invasive indicator, avoids modal editing mode complexity while still providing discoverability.
- Alternatives considered: Full modal mode (insert/normal), but that adds complexity and learning burden.

---

## Implementation Notes / Best Practices
- Use Textual `on_key` or `on_key_press` handlers in the `TaskListWidget` and return early when the focused widget is an input field.
- Implement a small `KeyBindingManager` in `src/gtasks_manager/tui/keybindings.py` to centralize mappings and allow toggling.
- Ensure background toggles use `@work` to perform the API call; update `Task` model status optimistically and revert on exception.
- Add unit tests for `KeyBindingManager` and integration tests for TUI navigation using `app.run_test()` pilot.
- Document any key conflicts in `specs/002-add-vim-keybindings/quickstart.md` and include instructions for disabling bindings.

---

## Research Tasks Generated
- Research: Best patterns for optimistic UI + background persistence in Textual apps.
- Research: Textual focus management and accessibility announcement patterns.
- Research: Testing patterns for key events using Textual pilot/test harness.

(Research complete — decisions captured above.)
