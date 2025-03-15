# **Changelog**

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.26] - 2025-01-08

### Added

- Performance
  - data compression using pako
  - implement progressive loading with LTTB (Largest-Triangle-Three-Buckets) sampling
  - intersection observer for lazy loading visualizations
  - optimized chunk sizes and sampling
  - loading progress indicator for large datasets
  - zlib compression on server side for data transfer optimization
  - lazy loading using intersection observer for on-demand graph renders
  - data sampling to reduce point density for large datasets
  - chunk loading to prevent browser freezing
  - memoization and React.memo to prevent unnecessary re-renders
  - debounced resize handling
  - feature toggles for fine-tuning optimization parameters
- Deployment
  - `preswald deploy` now works for local and cloud deployment via cloud-run
  - `preswald stop` works for stopping local deployments
- Misc
  - Moved setuptools from dev to core dependency in response to our first [github issue](https://github.com/StructuredLabs/preswald/issues/28)

## [0.1.23] - 2025-01-04

### Added

- Set log levels via preswald.toml + CLI

## [0.1.22] - 2025-01-03

### Added

- MVP of State Management
  - Atom and Workflow classes provide notebook-like DAGs
  - Support for selective recomputation, caching
  - Basic dependency visualization and analysis

## [0.1.0] - 2024-12-20

### Added

- Initial release of Preswald:
  - Core functionality for building simple, interactive data apps.
  - Support for Markdown, data connections, and rendering tables.
  - Basic theming and layout configurations.
  - Full CLI support for project management.
