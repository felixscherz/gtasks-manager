# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- VIM-style keybindings for TUI navigation (h/j/k/l) and task toggle (Enter)
- Optimistic UI updates for task completion with background persistence
- KeyBindingManager for managing VIM key mappings
- UI Focus representation for tracking selection and pane focus
- Accessibility announcements on focus changes
- VIM status indicator in TUI header

### Changed
- Updated Task and TaskList models to support Optional datetime fields
- Integrated KeyBindingManager into TasksApp for key handling
- Updated developer workflow to use `uv` for dependency management

### Fixed
- Fixed key handling to respect input widget focus
- Fixed toggle completion to revert on API failure
