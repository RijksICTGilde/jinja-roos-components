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

# [0.1] - 2025-11-04
- First tagged version
