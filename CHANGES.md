# [Unreleased]
- Added conversion scripts for automatic conversion from React (RVO) to jinja components
- Added support for general attributes that control margins, padding and font style which can be applied to any component
- Added some new convenience components, like c-strong c-p c-em which mimic html like structure but with RVO support (thus adding classes)
- Added the progress tracker component
- Passthrough for certain attributes like data-, aria-, hx-
- Fixed custom web data attributes: no conversion from camelcase
- Fixed support to always allow 'class' and 'id' to pass through
- Fixed automatic conversion for ol/ul elements and added a test for it
- Fixed automatic conversion for buttons
- Fixed automatic conversion for the action-group
- Reverted the layout-flow component, auto-generation broke it 
- make tests run with `python -m pytest tests/`
- add error handling around shorthand non-boolean attributes
- add support for shorthand boolean attributes
- read version number from toml
- source_path in component definition relative to rvo instead of absolute path
- move component definitions to src/jinja-roos-components/definitions
- update conversion script and autocomplete generation script to use new paths
- add `regenerate_components` script to run conversion on all converted components at once
- add tests for all components, some commented out because currently failing

# [0.1] - 2025-11-04
- First tagged version
