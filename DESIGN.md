# DESIGN.md

- Purpose: Define the product-specific UI and interaction design system for the visual storytelling app.
- Owner: Design lead and frontend maintainers.
- When to read: Before designing screens, styling components, naming UI states, or changing how the storytelling flow feels.
- Decisions that belong here: Visual direction, layout behavior, component styling, motion, accessibility, content tone, and presentation rules for the storytelling workspace.

This document follows the repository design-reference style while adapting it to a grounded multi-image storytelling workflow. It complements, but does not override, the higher-priority project and architecture documents.

## 1. Product Experience Goal

The app should feel like a small storytelling studio:
- users bring a sequence of images,
- the system studies them carefully,
- a short story is written with visible grounding,
- intermediate reasoning stays inspectable but not intrusive.

The experience should not feel like:
- a generic file uploader,
- a prompt playground,
- a dashboard full of technical panels,
- a magical black box that jumps straight to prose.

The best emotional target is:
- calm,
- trustworthy,
- editorial,
- a little cinematic,
- clearly structured.

## 2. Experience Principles

### 2.1 Sequence Is The Spine
The ordered image sequence is the primary input, so order must stay visually obvious at every important step.

### 2.2 Story First, Trace Second
The generated title and story should be the main result. Debug information must be available, but secondary.

### 2.3 Grounding Must Feel Visible
The UI should make it easy to see that the system observed scenes before writing. Analysis and evaluation should look inspectable, not hidden.

### 2.4 Sentiment Shapes Atmosphere, Not Truth
Sentiment can change tone, wording, and finishing feel, but it should not visually imply that the app invents facts.

### 2.5 Calm Beats Clutter
Use a small number of strong surfaces with clear hierarchy instead of many equally loud cards, borders, and controls.

### 2.6 The UI Stays Thin
The interface should express the pipeline clearly, but it must not look or behave like the place where narrative policy lives.

## 3. Visual Direction

Theme name: Storyboard Atelier

This UI should feel like an editorial storyboard desk rather than an analytics tool. The atmosphere is warm, tactile, and composed. Images should carry visual weight. Generated prose should feel like it belongs on a reading surface, while debug information should feel careful and structured.

Visual characteristics:
- warm paper-toned backgrounds,
- serif-led headings,
- image-first composition,
- restrained accent colors,
- clear order badges and sequence cues,
- trust-building trace panels,
- minimal chrome around the story result.

Avoid:
- neon or glossy UI,
- dark cyber aesthetics,
- purple-on-white defaults,
- enterprise blue-gray dashboards,
- overly cute scrapbook styling.

## 4. Color System

Use light mode as the primary MVP target.

### Core colors

- Story Ink: `#201a17`
- Terracotta Accent: `#c55c38`
- Studio Teal: `#3f6f6a`
- Paper Base: `#f6f1e8`
- Ivory Surface: `#fffaf2`
- Warm Sand: `#efe5d6`
- Ink Muted: `#635851`
- Border Linen: `#d8ccbc`
- Dusty Accent: `#f2c4af`
- Mist Teal: `#c7ddd9`
- Success Moss: `#4f7a56`
- Warning Clay: `#a45a2a`
- Error Brick: `#9a3f35`

### Color usage rules

- `Terracotta Accent` is for the main action, selected emphasis, and small high-priority highlights.
- `Studio Teal` is for analysis, traceability, and system-understanding surfaces.
- Keep background and neutral tones warm, not clinical.
- Do not recolor the whole interface per sentiment. Sentiment is content-level tone, not a theme switch.
- Use semantic colors only where state meaning matters.

```css
:root {
  --color-bg: #f6f1e8;
  --color-surface: #fffaf2;
  --color-surface-strong: #efe5d6;
  --color-ink: #201a17;
  --color-ink-muted: #635851;
  --color-border: #d8ccbc;
  --color-accent: #c55c38;
  --color-accent-soft: #f2c4af;
  --color-support: #3f6f6a;
  --color-support-soft: #c7ddd9;
  --color-success: #4f7a56;
  --color-warning: #a45a2a;
  --color-danger: #9a3f35;
}
```

## 5. Typography

### Font families

- Headline / narrative: `Fraunces`, fallback `Georgia`, serif
- Body / UI: `IBM Plex Sans`, fallback `Arial`, sans-serif
- Technical detail / trace: `IBM Plex Mono`, fallback `Menlo`, monospace

### Type scale

| Role | Font | Size | Weight | Line Height | Usage |
|------|------|------|--------|-------------|-------|
| Display Title | Fraunces | `clamp(2.4rem, 4vw, 3.6rem)` | 600 | 1.08 | Workspace title and major hero lines |
| Section Heading | Fraunces | `1.75rem` to `2.2rem` | 600 | 1.15 | Major section anchors |
| Card Title | Fraunces | `1.25rem` to `1.5rem` | 600 | 1.2 | Story panel, upload panel, debug sections |
| Body Large | IBM Plex Sans | `1.125rem` | 400 | 1.65 | Intro and support copy |
| Body Standard | IBM Plex Sans | `1rem` | 400 | 1.55 | Default controls and explanations |
| UI Label | IBM Plex Sans | `0.875rem` | 500 | 1.4 | Chips, form labels, tags |
| Metadata | IBM Plex Sans | `0.75rem` | 400 | 1.4 | Filenames, helper copy |
| Technical Snippet | IBM Plex Mono | `0.8125rem` | 400 | 1.5 | Structured debug content |

### Typography rules

- Use serif to create narrative and structural emphasis, not for every label.
- Keep body copy readable and relaxed.
- The story text itself should read comfortably in one pass, with a narrower measure than utility UI text.
- Use monospace only where structured trace data benefits from it.

## 6. Layout Model

### Overall structure

The MVP should work as a single main workspace rather than a multi-page product. The page should communicate a clear flow from input to result.

Desktop layout:
- left side: upload sequence and optional observation trace
- right side: sentiment controls, generate action, story output, evaluation summary

Mobile layout:
- single-column flow
- upload and sequence first
- sentiment and generate action second
- story result third
- debug sections last

### Container behavior

- Max content width: around `1200px`
- Comfortable horizontal padding: `24px` to `32px` on desktop
- Section rhythm should feel editorial, with larger spacing between major surfaces than between controls inside a surface

### Spacing scale

- Base unit: `8px`
- Preferred steps: `4, 8, 12, 16, 24, 32, 48, 64`

### Border radius scale

- `8px`: tight metadata pills
- `12px`: inputs and buttons
- `16px`: cards and standard panels
- `24px`: featured story surface or hero container

## 7. Core Screen Surfaces

### 7.1 Session Header

Contains:
- product title,
- one-sentence explanation,
- current workflow state,
- optional reset action.

The header should orient the user quickly without pushing the main workflow too far down the screen.

### 7.2 Upload And Sequence Surface

This is one of the most important surfaces in the app.

Requirements:
- make image order unmistakable,
- show thumbnails prominently,
- display order badges clearly,
- keep filenames and metadata secondary,
- allow room for future reordering controls.

The upload area should feel like arranging storyboard frames, not attaching files to a form.

### 7.3 Sentiment Selection Surface

Use pill-like chips or segmented controls, not a visually dull dropdown for the primary MVP interaction.

Requirements:
- small curated set of options,
- selected state is visually obvious,
- short helper text explains that sentiment affects style, not facts.

### 7.4 Story Output Surface

This is the main reading panel.

Requirements:
- title first,
- story text second,
- generous padding,
- moderate line length,
- understated border and soft elevation,
- nearby but visually secondary regenerate controls.

This panel should feel like a finished reading surface, not a generic result box.

### 7.5 Trace And Debug Surfaces

These surfaces show:
- scene observations,
- sequence memory,
- evaluation report,
- uncertainty notes when available.

Requirements:
- hidden behind accordions or expandable panels by default,
- structured and scannable,
- visibly separate observed facts from uncertainty or evaluation notes,
- secondary to the story result.

### 7.6 Error And Status Surface

Errors and progress should have their own clear presentation instead of blending into output text.

Requirements:
- visible stage naming during progress,
- clear recovery guidance for input errors,
- readable failure banners,
- technical detail available when needed without overwhelming the main message.

## 8. Component Styling

### Primary Button

- Background: `Terracotta Accent`
- Text: `Ivory Surface`
- Radius: `12px`
- Padding: `10px 16px`
- Use: generate story, confirm major action

### Secondary Button

- Background: `Warm Sand`
- Text: `Story Ink`
- Border: `1px solid Border Linen`
- Radius: `12px`

### Quiet Utility Button

- Background: transparent or `Ivory Surface`
- Text: `Ink Muted`
- Radius: `10px`

### Upload Dropzone

- Surface: `Ivory Surface`
- Border: `1px dashed Border Linen`
- Radius: `16px`
- Include short instructional copy and a confident empty-state message

### Sequence Card

- Surface: `Ivory Surface`
- Border: `1px solid Border Linen`
- Radius: `16px`
- Thumbnail-first layout
- Prominent order badge
- Clear hover or focus ring

### Sentiment Chip

- Default: `Ivory Surface` with `Border Linen`
- Selected: `Warm Sand` background with `Terracotta Accent` emphasis
- Radius: full pill or `999px`

### Story Panel

- Surface: `Ivory Surface`
- Border: `1px solid Border Linen`
- Radius: `24px`
- Optional whisper shadow for featured emphasis

### Debug Accordion

- Surface: `Ivory Surface` or `Mist Teal`
- Border: `1px solid Border Linen`
- Radius: `16px`
- Header should be compact and readable
- Expanded content should group fields by meaning, not dump raw blobs first

### Tags And Field Badges

Useful labels:
- `entities`
- `setting`
- `objects`
- `actions`
- `mood`
- `uncertainty`

Use `Studio Teal` and `Mist Teal` for trace-oriented badges, with warm neutrals for supporting metadata.

## 9. State Presentation

### Empty state

Show:
- a welcoming explanation,
- upload affordance,
- one sentence explaining what the system will do.

Do not show empty debug panels before the user has done anything.

### Partial input state

Show uploaded images and selected sentiment status clearly. The main action should explain what is still needed if generation is blocked.

### Ready state

The generate action should feel obvious and high-confidence.

### Loading state

The UI should name the current stage, such as:
- analyzing images
- linking sequence
- drafting story
- evaluating result

Use subtle animation, not noisy spinner overload.

### Completed state

Show the story first, then let the user open trace details.

### Error state

Use calm, clear language. The system should explain whether the issue is:
- missing input,
- invalid sentiment,
- missing API key,
- provider failure,
- pipeline failure.

### Regeneration state

If the user regenerates:
- keep the previous story visible until the new one is ready,
- preserve the sequence context,
- avoid resetting the page unnecessarily.

## 10. Motion

Motion should be restrained and purposeful.

Recommended motion:
- slight fade-and-rise on page or card entry,
- gentle progress transitions between pipeline stages,
- smooth accordion reveal for trace panels,
- subtle highlight when a new story replaces an old one.

Avoid:
- bouncing motion,
- flashy progress gimmicks,
- decorative animation unrelated to workflow state.

## 11. Accessibility Rules

- Maintain accessible contrast for text and controls.
- Never rely on color alone to show order, status, or selection.
- Use visible labels for upload order and stage progress.
- Minimum touch target: `44x44px`
- Keyboard users must be able to reach upload controls, sentiment chips, generate action, and debug accordions cleanly.
- Story text should keep a comfortable reading measure and line-height.

## 12. Responsive Rules

### Breakpoints

| Name | Width | Behavior |
|------|-------|----------|
| Mobile | `< 640px` | Single-column, larger touch targets, stacked panels |
| Tablet | `640px - 1023px` | Condensed two-zone layout, reduced side-by-side density |
| Desktop | `1024px+` | Full two-pane storytelling workspace |

### Mobile behavior

- Sequence cards stack vertically.
- Sentiment chips wrap cleanly.
- Story panel stays visually distinct from debug panels.
- Debug sections stay collapsible and secondary.
- Primary action remains easy to find without excessive scrolling.

## 13. Content Tone

Labels and helper copy should sound:
- clear,
- calm,
- specific,
- lightly editorial,
- never overhyped.

Good examples:
- `Generate story`
- `Observed scenes`
- `Sequence notes`
- `Evaluation summary`
- `Tone shapes style, not facts`

Bad examples:
- `Unleash the magic`
- `AI genius mode`
- `Narrative engine complete`

Error copy should be human and useful:
- say what failed,
- say what the user can try next,
- avoid unnecessary jargon.

## 14. Do And Don't

### Do

- make image order extremely clear,
- keep the story panel visually primary,
- show intermediate reasoning as optional trace surfaces,
- use warm neutrals and restrained accents,
- let the app feel inspectable and trustworthy,
- preserve calm reading rhythm across desktop and mobile.

### Don't

- do not let debug data dominate the first screen,
- do not make the interface look like a raw developer console,
- do not hide grounding failures behind pretty prose,
- do not use sentiment as a justification for loud theme changes,
- do not bury the main action or the story result,
- do not collapse everything into one dense panel.

## 15. Agent Build Guide

### Quick token reference

- Page background: `Paper Base (#f6f1e8)`
- Panel surface: `Ivory Surface (#fffaf2)`
- Strong surface: `Warm Sand (#efe5d6)`
- Primary ink: `Story Ink (#201a17)`
- Secondary text: `Ink Muted (#635851)`
- Primary action: `Terracotta Accent (#c55c38)`
- Trace accent: `Studio Teal (#3f6f6a)`
- Border: `Border Linen (#d8ccbc)`

### Prompt shorthand for implementation

- "Build a warm editorial storytelling workspace with a storyboard-style upload rail and a reading-focused story panel."
- "Use Fraunces for headings, IBM Plex Sans for UI text, and IBM Plex Mono only for structured debug snippets."
- "Keep trace panels collapsible and secondary to the generated story."
- "Make order badges unmistakable on every uploaded image card."
- "Use terracotta for the main story action and teal for analysis-oriented details."

## 16. Boundaries

- `DESIGN.md` defines how the product should look and feel.
- [docs/03_product/ui-information-architecture.md](/Users/sarahc/Downloads/SentimentAnalysis_3/docs/03_product/ui-information-architecture.md) defines what appears on screen and how the main areas are organized.
- [projects/visual-storytelling/SKILLS/ui-flow.SKILL.md](/Users/sarahc/Downloads/SentimentAnalysis_3/projects/visual-storytelling/SKILLS/ui-flow.SKILL.md) defines implementation-sensitive interaction rules.
- `DESIGN.md` does not define service logic, prompt contracts, or business rules.
