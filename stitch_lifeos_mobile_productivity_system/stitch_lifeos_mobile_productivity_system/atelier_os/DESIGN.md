---
name: Atelier OS
colors:
  surface: '#121316'
  surface-dim: '#121316'
  surface-bright: '#38393c'
  surface-container-lowest: '#0d0e11'
  surface-container-low: '#1b1b1f'
  surface-container: '#1f1f23'
  surface-container-high: '#292a2d'
  surface-container-highest: '#343538'
  on-surface: '#e3e2e6'
  on-surface-variant: '#d0c5b5'
  inverse-surface: '#e3e2e6'
  inverse-on-surface: '#2f3034'
  outline: '#998f81'
  outline-variant: '#4d463a'
  surface-tint: '#e3c284'
  primary: '#e3c284'
  on-primary: '#402d00'
  primary-container: '#c6a76b'
  on-primary-container: '#513c09'
  inverse-primary: '#735b26'
  secondary: '#e7c181'
  on-secondary: '#422d00'
  secondary-container: '#5c420e'
  on-secondary-container: '#d4b072'
  tertiary: '#7dd9a3'
  on-tertiary: '#003920'
  tertiary-container: '#61bd89'
  on-tertiary-container: '#004a2b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdea2'
  primary-fixed-dim: '#e3c284'
  on-primary-fixed: '#261900'
  on-primary-fixed-variant: '#5a4311'
  secondary-fixed: '#ffdea9'
  secondary-fixed-dim: '#e7c181'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5c420e'
  tertiary-fixed: '#99f6be'
  tertiary-fixed-dim: '#7dd9a3'
  on-tertiary-fixed: '#002111'
  on-tertiary-fixed-variant: '#005231'
  background: '#121316'
  on-background: '#e3e2e6'
  surface-variant: '#343538'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.06em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system embodies the ethos of a private executive sanctuary: a disciplined, distraction-free digital space built for deep intentionality and personal agency. Tailored for discerning knowledge workers, founders, and deliberate individuals, the aesthetic merges the razor-sharp functional clarity of tools like Linear and Things 3 with the calm, ritualistic atmosphere of bespoke physical planners and mechanical horology.

The visual direction is **Architectural Minimalist with Subdued Luminescence**. Surfaces are layered in velvety obsidian and dark charcoal tones, punctuated not by loud neon signifiers, but by meticulous micro-strokes of brushed brass and soft champagne gold. The emotional impact should be immediate mental de-cluttering: sovereign control, quiet luxury, precision, and architectural permanence.

## Colors

The palette relies on a tonal stepping system designed for low eye strain across prolonged desktop and mobile focus sessions:

- **Canvas & Structure**: Base canvas `#101114` anchors full-screen views, transitioning to `#17191E` for sidebars and top bars. Content containers and cards utilize `#1E2027`, lifting to `#262933` on interaction, selection, or elevated modals.
- **Accents**: The signature gold (`#C6A76B`) represents intention, active states, progress, and achievement. The secondary soft champagne (`#DFBA7B`) is reserved for highlights, active indicator pips, and hover states.
- **Borders & Dividers**: Structural boundaries are governed strictly by `#282B34`, maintaining clean line-work without optical heaviness.
- **Text & Hierarchy**: Primary typography `#F5F5F5` commands high contrast against deep surfaces, while `#92949E` provides deliberate low-distraction reading for metadata, timestamps, and secondary descriptions.
- **Functional Semantics**: Feedback cues are muted yet unambiguous—`#4EAA78` (Success / Completed), `#E5A93B` (Warning / Due Soon), and `#E05D52` (Urgent / Overdue / High Priority).

## Typography

The type system blends the human-scaled geometric precision of **Plus Jakarta Sans** for textual narrative with the surgical discipline of **JetBrains Mono** for numerical values, keyboard accelerators, timers, and operational metrics.

- **Tabular Numerals**: Timers, progress percentages, streak tallies, and deadline countdowns must always be rendered with fixed-width tabular figures (`tnum` font feature) to eliminate optical layout shift.
- **Case Rules**: High-level system headers and body descriptions use sentence case. Status tags, keyboard shortcuts, and mono metadata employ subtle uppercase styling with generous tracking to aid immediate visual parsing.

## Layout & Spacing

The structural layout adapts fluidly between mouse-driven wide workspaces and gesture-first Android handhelds:

- **Desktop Layout**: Collapsible dual-tier split: a fixed 240px navigation sidebar anchored to the left, paired with an infinitely scrollable or kanban/timeline-organized main viewport. Canvas constraints default to a max container width of 1440px for focused productivity views.
- **Mobile Layout**: Bottom-anchored ergonomics with a fixed tab bar and bottom-sheet drawers for complex modals. Margins conform to `1rem` on narrow viewports to maximize line length while preserving thumb boundaries.
- **Spatial Rhythm**: All margins, paddings, and layout gaps adhere strictly to an 8pt base grid (with a 4pt sub-unit for compact chip paddings and icon offsets). Internal card padding defaults to `space-md` (16px) on mobile and expands to `space-lg` (24px) for desktop summary panels.

## Elevation & Depth

Visual hierarchy does not use exaggerated blurry drop shadows; it relies on **chiseled surfaces and tonal luminance tiers**:

- **Tier 0 (Base)**: `#101114` canvas. Completely flat.
- **Tier 1 (Resting Surface)**: `#1E2027` with a crisp `1px solid #282B34` border. No drop shadow.
- **Tier 2 (Elevated & Hover)**: `#262933` background with a subtle ambient shadow (`0 8px 24px rgba(0, 0, 0, 0.45)`) combined with a hairline top highlight stroke (`border-top: 1px solid rgba(255, 255, 255, 0.06)`).
- **Tier 3 (Floating Overlays, Drawers & Menus)**: `#1E2027` with backdrop-filter blur (`16px`), an outer border of `#282B34`, and an atmospheric depth shadow (`0 20px 48px rgba(0, 0, 0, 0.7)`).

## Shapes

The geometric architecture uses tailored corner radii to separate content containers from interactive micro-triggers:

- **Cards & Modal Containers**: Defined with `rounded-2xl` (16px) corner radiuses to establish soft, inviting, yet structured blocks.
- **Inputs, Search Bars, & Field Groups**: Anchored with `rounded-xl` (12px) for structured affordance.
- **Pills, Badges, Status Dots, & Action Buttons**: Strictly `rounded-full` (9999px) to establish tactile micro-elements that contrast with the structural rectangularity of the cards.

## Components

### Buttons
- **Primary Action (Luxury Gold)**: Background `#C6A76B`, foreground `#101114`, font-weight 600. On hover: `#DFBA7B`. Active scale transition: 0.98.
- **Secondary / Ghost**: Background `transparent`, border `1px solid #282B34`, text `#F5F5F5`. On hover: background `#262933`, border `#C6A76B`.
- **Quick Add Floating Action Button (FAB)**: Mobile-centric 56x56px circular component positioned floating above the bottom navigation bar. Solid `#C6A76B` background, containing an obsidian `+` glyph. Subtle amber-gold glow aura (`0 0 24px rgba(198, 167, 107, 0.3)`).

### Bottom Navigation Bar (Android)
- Height: 64px + safe area inset.
- Background: `#17191E` with a hairline top border of `1px solid #282B34` and 12px blur backdrop.
- 5 items: **Home**, **Tasks**, **Projects**, **Calendar**, **More**.
- Inactive items use `#92949E`; the active route glows softly in `#C6A76B` with a 3px horizontal brass indicator pill placed below the icon.

### Cards & Task Rows
- **Card**: Surface `#1E2027`, radius 16px, 1px border `#282B34`. Padding 16px.
- **Task Row**: Interactive item with integrated checkbox. Displays inline priority pill, project indicator, and JetBrains Mono due-date string. Hover transitions background to `#262933`.

### Priority Badges
Compact, pill-shaped tags (`rounded-full`) with uppercase mono text:
- **Urgent**: `#E05D52` background at 12% opacity, text `#E05D52`, border `1px solid rgba(224, 93, 82, 0.25)`.
- **High**: `#E5A93B` background at 12% opacity, text `#E5A93B`, border `1px solid rgba(229, 169, 59, 0.25)`.
- **Medium**: `#C6A76B` background at 12% opacity, text `#C6A76B`, border `1px solid rgba(198, 167, 107, 0.25)`.
- **Low**: Background `rgba(146, 148, 158, 0.1)`, text `#92949E`, border `1px solid #282B34`.

### Streak Counter & Metrics
- Inline pill containing a brass/flame glyph, accompanied by tabular numerals (e.g., `14d`). Fill highlights use `#C6A76B` with a subtle linear gradient fading into `#DFBA7B`.

### Progress Bars
- Height: 4px track with a `#282B34` background and full radius. Active fill uses a `#C6A76B` solid brass fill with smooth cubic-bezier easing during updates.

### Checkboxes
- 18x18px rounded rectangle (radius 5px). Idle state: `1.5px solid #282B34`, background transparent.
- Checked state: `#C6A76B` fill, `#101114` checkmark icon, accompanied by smooth strikethrough transition on adjacent primary text.