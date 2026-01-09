# Data Model: VIM Keybindings Feature

This document describes entities introduced or affected by the VIM keybindings feature.

## Entities

- Task
  - Fields (existing):
    - `id`: str (immutable)
    - `title`: str
    - `status`: str, enum {`needsAction`, `completed`}
    - `notes`: Optional[str]
    - `due`: Optional[datetime]
  - Validation:
    - `title` non-empty
    - `status` must be one of `needsAction` or `completed`

- UI Focus (new lightweight concept)
  - Fields:
    - `pane`: str enum {`sidebar`, `task_list`, `details`, `input`}
    - `index`: Optional[int] — index of selected item in the focused pane
  - Validation:
    - `index` must be >= 0 when present and less than pane length

- KeyBindingManager (configuration)
  - Fields:
    - `enabled`: bool (default True)
    - `mappings`: Dict[str, str] mapping key -> action (e.g., `{'j': 'move_down'}`)
  - Validation:
    - `mappings` keys must be single-character strings

## State Transitions

- Toggling task completion (`Enter` action):
  - FROM: `needsAction` -> TO: `completed`
  - FROM: `completed` -> TO: `needsAction`
  - Side effects:
    - UI: optimistic update of `status` field and visual indicator
    - Background: API call to persist change; on failure, revert `status` and show transient error

- Navigation keys (`j/k/h/l`):
  - `j`: `index` += 1 (bounded by pane length)
  - `k`: `index` -= 1 (bounded by >= 0)
  - `h`: change `pane` to left neighbor if exists; adjust `index` accordingly
  - `l`: change `pane` to right neighbor if exists; adjust `index` accordingly

## Tests implied by model
- Unit tests: `KeyBindingManager` mapping validity and toggle behavior
- Integration tests: TUI navigation updates `UI Focus` correctly and `Enter` toggles `Task.status` with optimistic update and rollback


(End of data model)
