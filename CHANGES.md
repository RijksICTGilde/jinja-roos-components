# [Unreleased]
- (!backwards incompatible) change of attribute `showIcon` ("no, "before", "after") to `iconPlacement` ("before", "after"). affected components: `button`, `link`, `tag`. The presence of the `icon` attribute is now enough to show (default "before")
- add customization options `css_class_mappings` and `attribute_removals`

# [0.2] - 2025-11-17
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
- raise an error on handling unknown components so we avoid entering a never ending lookup loop
- add docs on component composition
- rename event_mixin to _generic_attributes and namespace from 'events' to 'attrs'
- fix attribute passthrough (data-*, aria-*, @events, hx-*) for all 58 components (26 were missing)
- added documentation in docs/ATTRIBUTE_PASSTHROUGH.md
- added setup so tests work on my machine: uv run pytest tests

# [0.1] - 2025-11-04
- First tagged version
