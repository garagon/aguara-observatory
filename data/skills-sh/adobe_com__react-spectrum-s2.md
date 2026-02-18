skills
/
adobe
/
com
/
react-spectrum-s2
react-spectrum-s2
$
npx skills add https://github.com/adobe/com --skill react-spectrum-s2
SKILL.md
React Spectrum S2 (Spectrum 2)
React Spectrum S2 is Adobe's implementation of the Spectrum 2 design system in React. It provides a collection of accessible, adaptive, and high-quality UI components.
Documentation Structure
The
references/
directory contains detailed documentation organized as follows:
Guides
Collections
: Many components display a collection of items, and provide functionality such as keyboard navigation, and selection. Learn how to load and render collections using React Spectrum's compositional API.
Forms
: Learn how to integrate with HTML forms, validate and submit data, and use React Spectrum with form libraries.
Getting started
: ## Installation
Migrating to Spectrum 2
: Learn how to migrate from React Spectrum v3 to Spectrum 2.
Selection
: Many collection components support selecting items by clicking or tapping them, or by using the keyboard. Learn how to handle selection events, how to control selection programmatically, and the data structures used to represent a selection.
Style Macro
: The  macro supports a constrained set of values per property that conform to Spectrum 2.
Styling
: Learn how to use the  macro to apply Spectrum tokens directly in your components with type-safe autocompletion.
Working with AI
: Learn how to use the React Spectrum MCP Server, Agent Skills, and more to help you build with AI.
Components
Accordion
: An accordion is a container for multiple accordion items.
ActionBar
: Action bars are used for single and bulk selection patterns when a user needs to perform actions on one or more items at the same time.
ActionButton
: ActionButtons allow users to perform an action.
ActionButtonGroup
: An ActionButtonGroup is a grouping of related ActionButtons.
ActionMenu
: ActionMenu combines an ActionButton with a Menu for simple "more actions" use cases.
Avatar
: An avatar is a thumbnail representation of an entity, such as a user or an organization.
AvatarGroup
: An avatar group is a grouping of avatars that are related to each other.
Badge
: Badges are used for showing a small amount of color-categorized metadata, ideal for getting a user's attention.
Breadcrumbs
: Breadcrumbs show hierarchy and navigational context for a user's location within an application.
Button
: Buttons allow users to perform an action.
ButtonGroup
: ButtonGroup handles overflow for a grouping of buttons whose actions are related to each other.
Calendar
: Calendars display a grid of days in one or more months and allow users to select a single date.
Card
: A Card summarizes an object that a user can select or navigate to.
CardView
: A CardView displays a group of related objects, with support for selection and bulk actions.
Checkbox
: Checkboxes allow users to select multiple items from a list of individual items,
CheckboxGroup
: A CheckboxGroup allows users to select one or more items from a list of choices.
ColorArea
: A ColorArea allows users to adjust two channels of an RGB, HSL or HSB color value against a two-dimensional gradient background.
ColorField
: A color field allows users to edit a hex color or individual color channel value.
ColorSlider
: A ColorSlider allows users to adjust an individual channel of a color value.
ColorSwatch
: A ColorSwatch displays a preview of a selected color.
ColorSwatchPicker
: A ColorSwatchPicker displays a list of color swatches and allows a user to select one of them.
ColorWheel
: A ColorWheel allows users to adjust the hue of an HSL or HSB color value on a circular track.
ComboBox
: ComboBox allow users to choose a single option from a collapsible list of options when space is limited.
ContextualHelp
: Contextual help shows a user extra information about the state of an adjacent component, or a total view.
DateField
: DateFields allow users to enter and edit date and time values using a keyboard.
DatePicker
: DatePickers combine a DateField and a Calendar popover to allow users to enter or select a date and time value.
DateRangePicker
: DateRangePickers combine two DateFields and a RangeCalendar popover to allow users
Dialog
: Dialogs are windows containing contextual information, tasks, or workflows that appear over the user interface.
Disclosure
: A disclosure is a collapsible section of content. It is composed of a header with a heading and trigger button, and a panel that contains the content.
Divider
: Dividers bring clarity to a layout by grouping and dividing content in close proximity.
DropZone
: A drop zone is an area into which one or multiple objects can be dragged and dropped.
Form
: Forms allow users to enter data that can be submitted while providing alignment and styling for form fields.
Icons
: React Spectrum offers a set of open source icons that can be imported from .
IllustratedMessage
: An IllustratedMessage displays an illustration and a message, usually
Illustrations
: React Spectrum offers a collection of illustrations that can be imported from .
Image
: An image with support for skeleton loading and custom error states.
InlineAlert
: Inline alerts display a non-modal message associated with objects in a view.
Link
: Links allow users to navigate to a different location.
LinkButton
: A LinkButton combines the functionality of a link with the appearance of a button. Useful for allowing users to navigate to another page.
mcp
Menu
: Menus display a list of actions or options that a user can choose.
Meter
: Meters are visual representations of a quantity or an achievement.
NumberField
: NumberFields allow users to input number values with a keyboard or increment/decrement with step buttons.
Picker
: Pickers allow users to choose a single option from a collapsible list of options when space is limited.
Popover
: A popover is an overlay element positioned relative to a trigger.
ProgressBar
: ProgressBars show the progression of a system operation: downloading, uploading, processing, etc., in a visual way.
ProgressCircle
: ProgressCircles show the progression of a system operation such as downloading, uploading, or processing, in a visual way.
Provider
: Provider is the container for all React Spectrum components.
RadioGroup
: Radio groups allow users to select a single option from a list of mutually exclusive options.
RangeCalendar
: RangeCalendars display a grid of days in one or more months and allow users to select a contiguous range of dates.
RangeSlider
: RangeSliders allow users to quickly select a subset range. They should be used when the upper and lower bounds to the range are invariable.
SearchField
: A SearchField is a text field designed for searches.
SegmentedControl
: A SegmentedControl is a mutually exclusive group of buttons used for view switching.
SelectBoxGroup
: SelectBoxGroup allows users to select one or more options from a list.
Skeleton
: A Skeleton wraps around content to render it as a placeholder.
Slider
: Sliders allow users to quickly select a value within a range. They should be used when the upper and lower bounds to the range are invariable.
StatusLight
: Status lights are used to color code categories and labels commonly found in data visualization.
Switch
: Switches allow users to turn an individual option on or off.
TableView
: Tables are containers for displaying information. They allow users to quickly scan, sort, compare, and take action on large amounts of data.
Tabs
: Tabs organize content into multiple sections and allow users to navigate between them. The content under the set of tabs should be related and form a coherent unit.
TagGroup
: Tags allow users to categorize content. They can represent keywords or people, and are grouped to describe an item or a search request.
TextArea
: A textarea allows a user to input mult-line text.
TextField
: TextFields are text inputs that allow users to input custom text entries
TimeField
: TimeFields allow users to enter and edit time values using a keyboard.
Toast
: A ToastContainer renders the queued toasts in an application. It should be placed
ToggleButton
: ToggleButtons allow users to toggle a selection on or off, for example
ToggleButtonGroup
: A ToggleButtonGroup is a grouping of related ToggleButtons, with single or multiple selection.
Tooltip
: Display container for Tooltip content. Has a directional arrow dependent on its placement.
TreeView
: A tree view provides users with a way to navigate nested hierarchical information.
Testing
Testing CheckboxGroup
Testing ComboBox
Testing Dialog
Testing Menu
Testing Picker
Testing RadioGroup
Testing TableView
Testing Tabs
Testing TreeView
Weekly Installs
66
Repository
adobe/com
First Seen
14 days ago
Security Audits
Gen Agent Trust Hub
Pass
Socket
Pass
Snyk
Pass
Installed on
codex
48
opencode
46
github-copilot
43
gemini-cli
40
kimi-cli
35
amp
35