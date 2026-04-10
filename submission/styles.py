from __future__ import annotations

APP_CSS = """
:root {
  --story-bg: #f6f1e8;
  --story-surface: #fffaf2;
  --story-surface-strong: #f2e9dc;
  --story-surface-raised: #fffdf9;
  --story-ink: #201a17;
  --story-ink-muted: #635851;
  --story-border: #d8ccbc;
  --story-border-strong: #c3b3a1;
  --story-accent: #c55c38;
  --story-accent-hover: #af4b29;
  --story-accent-active: #963f24;
  --story-accent-soft: #f7d8c8;
  --story-support: #3f6f6a;
  --story-support-soft: #dceae6;
  --story-success: #4f7a56;
  --story-success-soft: #dbe8dc;
  --story-warning: #a45a2a;
  --story-warning-soft: #f4e2d2;
  --story-danger: #9a3f35;
  --story-danger-soft: #f2ddd9;
  --story-shadow-card: 0 18px 44px rgba(77, 60, 43, 0.08);
  --story-shadow-soft: 0 12px 26px rgba(77, 60, 43, 0.06);
  --story-shadow-button: 0 10px 20px rgba(77, 60, 43, 0.08);
  --story-shadow-button-hover: 0 14px 28px rgba(77, 60, 43, 0.12);
  --story-radius-button: 14px;
  --story-radius-card: 18px;
  --story-radius-panel: 24px;
  --sentiment-happy: #f59e0b;
  --sentiment-happy-soft: #fff4cc;
  --sentiment-sad: #3b82f6;
  --sentiment-sad-soft: #dbeafe;
  --sentiment-suspenseful: #7c3aed;
  --sentiment-suspenseful-soft: #ede9fe;
  --sentiment-mysterious: #0f766e;
  --sentiment-mysterious-soft: #ccfbf1;
  --sentiment-heartwarming: #e11d48;
  --sentiment-heartwarming-soft: #ffe4e6;
  --sentiment-playful: #16a34a;
  --sentiment-playful-soft: #dcfce7;
}

html,
body,
.gradio-container,
body > gradio-app {
  background: radial-gradient(circle at top, #fffdf8 0%, var(--story-bg) 56%, #ece2d3 100%);
  color-scheme: light;
}

html,
body {
  min-height: 100%;
  overflow-x: hidden;
}

body,
.gradio-container {
  --background-fill-primary: #f6f1e8 !important;
  --background-fill-secondary: #fffaf2 !important;
  --block-background-fill: #fffaf2 !important;
  --block-border-color: #d8ccbc !important;
  --body-text-color: #201a17 !important;
  --body-text-color-subdued: #635851 !important;
  --input-background-fill: #fffdf9 !important;
  --button-secondary-background-fill: #fffaf2 !important;
  --button-secondary-text-color: #201a17 !important;
  color: var(--story-ink);
  font-family: "IBM Plex Sans", Arial, sans-serif;
}

body.dark,
body.dark .gradio-container,
body.dark body > gradio-app {
  background: radial-gradient(circle at top, #ffffff 0%, var(--story-bg) 58%, #e9edf2 100%) !important;
  color: var(--story-ink) !important;
  color-scheme: light !important;
}

.gradio-container .main.fillable.app {
  background: transparent !important;
}

.gradio-container input:not([type="file"]),
.gradio-container textarea,
.gradio-container select {
  background: var(--story-surface-raised) !important;
  border-color: var(--story-border) !important;
  border-radius: var(--story-radius-button) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  color: var(--story-ink) !important;
}

body.dark .gradio-container [data-testid="block-label"],
.gradio-container [data-testid="block-label"],
body.dark .gradio-container .file-preview-holder,
.gradio-container .file-preview-holder,
body.dark .gradio-container .file-preview,
.gradio-container .file-preview,
body.dark .gradio-container .file-preview td,
.gradio-container .file-preview td,
body.dark .gradio-container .file-preview span,
.gradio-container .file-preview span,
body.dark .gradio-container .file-preview a,
.gradio-container .file-preview a {
  color: var(--story-ink) !important;
}

.panel-card .styler {
  background: transparent !important;
  box-shadow: none !important;
}

body.dark .gradio-container [data-testid="block-label"],
.gradio-container [data-testid="block-label"] {
  background: transparent !important;
}

body.dark .gradio-container .file-preview-holder,
.gradio-container .file-preview-holder {
  background: var(--story-surface-raised) !important;
  border-top: 1px solid var(--story-border) !important;
}

body.dark .gradio-container .file-preview,
.gradio-container .file-preview {
  background: transparent !important;
  border-collapse: collapse !important;
  width: 100% !important;
}

body.dark .gradio-container .file-preview tr.file,
.gradio-container .file-preview tr.file {
  background: var(--story-surface-raised) !important;
}

body.dark .gradio-container .file-preview tr.file:nth-child(odd),
.gradio-container .file-preview tr.file:nth-child(odd) {
  background: var(--story-surface-strong) !important;
}

body.dark .gradio-container .file-preview tr.file + tr.file,
.gradio-container .file-preview tr.file + tr.file {
  border-top: 1px solid var(--story-border) !important;
}

body.dark .gradio-container .file-preview .label-clear-button,
.gradio-container .file-preview .label-clear-button {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  color: var(--story-ink-muted) !important;
  min-height: auto !important;
  padding: 0 6px !important;
}

body.dark .gradio-container .file-preview .label-clear-button:hover,
.gradio-container .file-preview .label-clear-button:hover {
  color: var(--story-ink) !important;
  transform: none !important;
}

.gradio-container input:not([type="file"]):focus-visible,
.gradio-container textarea:focus-visible,
.gradio-container select:focus-visible {
  outline: 2px solid rgba(197, 92, 56, 0.42) !important;
  outline-offset: 2px;
}

.gradio-container {
  box-sizing: border-box;
  margin: 0 auto !important;
  max-width: 1680px !important;
  padding: 0 24px 40px;
  width: 100% !important;
}

body > gradio-app {
  display: block;
  min-height: 100vh;
}

.visually-hidden {
  border: 0 !important;
  clip: rect(0 0 0 0) !important;
  clip-path: inset(50%) !important;
  height: 1px !important;
  margin: -1px !important;
  overflow: hidden !important;
  padding: 0 !important;
  position: absolute !important;
  white-space: nowrap !important;
  width: 1px !important;
}

.studio-shell {
  padding: 24px 0 10px;
}

.studio-header {
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.97), rgba(255, 250, 242, 0.95));
  border: 1px solid rgba(216, 204, 188, 0.94);
  border-radius: 28px;
  padding: 28px 30px;
  box-shadow: 0 24px 60px rgba(77, 60, 43, 0.08);
}

.studio-kicker {
  color: var(--story-support);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin: 0 0 10px;
  text-transform: uppercase;
}

.studio-header h1 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: clamp(2.4rem, 4vw, 3.5rem);
  line-height: 1.05;
  margin: 0;
}

.studio-header p {
  color: var(--story-ink-muted);
  font-size: 1.02rem;
  line-height: 1.65;
  margin: 14px 0 0;
  max-width: 760px;
}

.panel-card {
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 250, 242, 0.98));
  border: 1px solid rgba(216, 204, 188, 0.95);
  border-radius: var(--story-radius-panel);
  min-width: 0;
  box-shadow: var(--story-shadow-card);
}

.input-panel,
.result-panel {
  padding: 24px;
}

.preview-shell {
  border-top: 1px solid var(--story-border);
  margin-top: 20px;
  padding-top: 20px;
}

.workspace-row,
.workspace-column {
  min-width: 0;
}

.workspace-row {
  align-items: flex-start;
  gap: 24px;
}

.workspace-input-column,
.workspace-result-column {
  position: relative;
}

.workspace-input-column {
  z-index: 2;
}

.workspace-result-column {
  z-index: 1;
}

[data-testid="status-tracker"] {
  pointer-events: none !important;
}

footer {
  display: none !important;
}

.gradio-container .main.fillable.app,
.gradio-container .wrap,
.gradio-container .contain {
  max-width: none !important;
  width: 100% !important;
}

.gradio-container .main.fillable.app {
  padding: 0 !important;
}

body.story-busy {
  cursor: progress;
}

body.story-busy::after {
  background: rgba(32, 26, 23, 0.88);
  border-radius: 999px;
  box-shadow: 0 16px 34px rgba(77, 60, 43, 0.18);
  color: #ffffff;
  content: attr(data-busy-label);
  font-size: 0.86rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  padding: 12px 18px;
  position: fixed;
  right: 24px;
  top: 24px;
  z-index: 9999;
}

body.story-busy #generate-button,
body.story-busy #regenerate-button,
body.story-busy #strict-regenerate-button,
body.story-busy #corrected-generate-button,
body.story-busy #corrected-strict-generate-button,
body.story-busy #clear-corrections-button {
  opacity: 0.72;
  pointer-events: none;
}

.action-row {
  align-items: stretch;
  display: flex;
  margin: 0 0 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.action-row > * {
  flex: 1 1 220px;
  min-width: 0;
}

.followup-row {
  margin-bottom: 12px;
}

.advanced-row {
  margin-bottom: 16px;
}

.primary-action-label,
.action-group-label {
  color: var(--story-ink-muted);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin: 8px 0 10px;
  text-transform: uppercase;
}

.action-group-label-muted {
  color: var(--story-support);
}

.action-guidance-shell {
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.96), rgba(247, 241, 232, 0.94));
  border: 1px solid rgba(216, 204, 188, 0.92);
  border-radius: 16px;
  margin: 0 0 18px;
  padding: 14px 16px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.action-guidance-shell.running {
  background: linear-gradient(180deg, rgba(250, 253, 252, 0.96), rgba(238, 246, 244, 0.94));
  border-color: rgba(63, 111, 106, 0.22);
}

.action-guidance-head {
  display: grid;
  gap: 8px;
}

.action-guidance-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 12px;
}

.action-guidance-item {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(216, 204, 188, 0.86);
  border-radius: 14px;
  padding: 12px;
}

.action-guidance-item.ready {
  border-color: rgba(79, 122, 86, 0.28);
}

.action-guidance-item.blocked {
  background: rgba(255, 250, 242, 0.82);
}

.action-guidance-item-head,
.action-guidance-alert {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: space-between;
}

.action-guidance-title {
  color: var(--story-ink);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.action-guidance-copy {
  color: var(--story-ink-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.action-guidance-label {
  color: var(--story-ink-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.action-guidance-action {
  color: var(--story-ink);
  font-size: 0.96rem;
  font-weight: 700;
  margin: 10px 0 6px;
}

.action-guidance-note {
  color: var(--story-ink-muted);
  font-size: 0.88rem;
  line-height: 1.55;
  margin: 0;
}

.action-guidance-pill {
  align-items: center;
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 5px 9px;
  text-transform: uppercase;
}

.action-guidance-pill.ready {
  background: rgba(79, 122, 86, 0.14);
  color: var(--story-success);
}

.action-guidance-pill.blocked {
  background: rgba(164, 90, 42, 0.14);
  color: var(--story-warning);
}

.action-guidance-pill.processing {
  background: rgba(63, 111, 106, 0.12);
  color: var(--story-support);
}

.section-title {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.45rem;
  line-height: 1.2;
  margin: 0 0 8px;
}

.section-copy {
  color: var(--story-ink-muted);
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0 0 18px;
}

.primary-cta-button,
.followup-button,
.advanced-button,
.quiet-button {
  align-items: center;
  background: var(--story-surface-raised) !important;
  border: 1px solid var(--story-border) !important;
  border-radius: var(--story-radius-button) !important;
  box-shadow: none !important;
  color: var(--story-ink) !important;
  display: flex;
  font-weight: 600;
  justify-content: center;
  line-height: 1.35;
  min-height: 48px;
  padding: 10px 16px !important;
  transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease;
  white-space: normal;
}

.primary-cta-button:hover:not(:disabled),
.primary-cta-button:hover:not([disabled]),
.followup-button:hover:not(:disabled),
.followup-button:hover:not([disabled]),
.advanced-button:hover:not(:disabled),
.advanced-button:hover:not([disabled]),
.quiet-button:hover:not(:disabled),
.quiet-button:hover:not([disabled]) {
  background: var(--story-surface) !important;
  border-color: var(--story-border-strong) !important;
}

#generate-button:hover:not(:disabled),
#generate-button:hover:not([disabled]) {
  background: var(--story-accent-hover) !important;
  border-color: #914122 !important;
}

#generate-button:active:not(:disabled),
#generate-button:active:not([disabled]) {
  background: var(--story-accent-active) !important;
}

.primary-cta-button:disabled,
.primary-cta-button[disabled],
.followup-button:disabled,
.followup-button[disabled],
.advanced-button:disabled,
.advanced-button[disabled],
.quiet-button:disabled,
.quiet-button[disabled] {
  background: var(--story-surface-strong) !important;
  border-color: rgba(195, 179, 161, 0.85) !important;
  color: rgba(99, 88, 81, 0.78) !important;
  opacity: 1 !important;
}

#generate-button:disabled,
#generate-button[disabled] {
  background: var(--story-surface-strong) !important;
  border-color: rgba(195, 179, 161, 0.92) !important;
  color: rgba(99, 88, 81, 0.82) !important;
}

#generate-button {
  background: var(--story-accent) !important;
  border-color: #a74928 !important;
  color: #fffaf2 !important;
  font-weight: 700;
  min-height: 50px;
}

#strict-regenerate-button {
  border-color: rgba(63, 111, 106, 0.26) !important;
}

#corrected-generate-button,
#corrected-strict-generate-button,
#clear-corrections-button {
  color: var(--story-ink-muted) !important;
}

#corrected-strict-generate-button {
  border-color: rgba(63, 111, 106, 0.22) !important;
  color: var(--story-ink) !important;
}

#clear-corrections-button {
  border-color: rgba(154, 63, 53, 0.18) !important;
  color: var(--story-danger) !important;
}

#sequence-helper {
  color: var(--story-support);
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin: 10px 0 12px;
  text-transform: uppercase;
}

#sentiment-choices label {
  --sentiment-accent: var(--story-accent);
  --sentiment-soft: var(--story-accent-soft);
  --checkbox-label-background-fill: var(--story-surface);
  --checkbox-label-background-fill-hover: var(--sentiment-soft);
  --checkbox-label-background-fill-selected: var(--sentiment-soft);
  --checkbox-label-border-color: var(--story-border);
  --checkbox-label-border-color-selected: var(--sentiment-accent);
  align-items: center;
  border-radius: 999px;
  color: var(--story-ink) !important;
  display: inline-flex;
  gap: 8px;
  margin: 4px 8px 4px 0;
  padding: 7px 12px;
  position: relative;
  text-transform: capitalize;
  transition: background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

#sentiment-choices input[type="radio"] {
  accent-color: var(--sentiment-accent);
  height: 14px;
  width: 14px;
}

#sentiment-choices label::before {
  align-items: center;
  background: var(--sentiment-soft);
  border-radius: 999px;
  color: var(--sentiment-accent);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 0.88rem;
  height: 24px;
  justify-content: center;
  line-height: 1;
  width: 24px;
}

#sentiment-choices label:has(input:checked) {
  background: var(--sentiment-soft) !important;
  background-color: var(--sentiment-soft) !important;
  background-image: none !important;
  border-color: var(--sentiment-accent);
  box-shadow: inset 0 0 0 999px var(--sentiment-soft), 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px var(--sentiment-accent);
  outline: 1px solid var(--sentiment-accent);
  outline-offset: 0;
  transform: translateY(-1px);
}

#sentiment-choices label.selected {
  background: var(--sentiment-soft) !important;
  background-color: var(--sentiment-soft) !important;
  background-image: none !important;
  border-color: var(--sentiment-accent) !important;
  box-shadow: inset 0 0 0 999px var(--sentiment-soft), 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px var(--sentiment-accent) !important;
  outline: 1px solid var(--sentiment-accent) !important;
  outline-offset: 0;
}

#sentiment-choices label:has(input:checked)::before {
  background: rgba(255, 255, 255, 0.98);
  color: var(--sentiment-accent);
}

#sentiment-choices label:nth-of-type(1)::before {
  content: "\\2600";
}

#sentiment-choices label:nth-of-type(1) {
  --sentiment-accent: var(--sentiment-happy);
  --sentiment-soft: var(--sentiment-happy-soft);
}

#sentiment-choices label:nth-of-type(2)::before {
  content: "\\263E";
}

#sentiment-choices label:nth-of-type(2) {
  --sentiment-accent: var(--sentiment-sad);
  --sentiment-soft: var(--sentiment-sad-soft);
}

#sentiment-choices label:nth-of-type(3)::before {
  content: "\\25B3";
}

#sentiment-choices label:nth-of-type(3) {
  --sentiment-accent: var(--sentiment-suspenseful);
  --sentiment-soft: var(--sentiment-suspenseful-soft);
}

#sentiment-choices label:nth-of-type(4)::before {
  content: "\\25CC";
}

#sentiment-choices label:nth-of-type(4) {
  --sentiment-accent: var(--sentiment-mysterious);
  --sentiment-soft: var(--sentiment-mysterious-soft);
}

#sentiment-choices label:nth-of-type(5)::before {
  content: "\\2665";
}

#sentiment-choices label:nth-of-type(5) {
  --sentiment-accent: var(--sentiment-heartwarming);
  --sentiment-soft: var(--sentiment-heartwarming-soft);
}

#sentiment-choices label:nth-of-type(6)::before {
  content: "\\2726";
}

#sentiment-choices label:nth-of-type(6) {
  --sentiment-accent: var(--sentiment-playful);
  --sentiment-soft: var(--sentiment-playful-soft);
}

#sentiment-choices label.selected:nth-of-type(1),
#sentiment-choices label:nth-of-type(1):has(input:checked) {
  background: #fff4cc !important;
  background-color: #fff4cc !important;
  border-color: #f59e0b !important;
  box-shadow: inset 0 0 0 999px #fff4cc, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #f59e0b !important;
  outline: 1px solid #f59e0b !important;
}

#sentiment-choices label.selected:nth-of-type(2),
#sentiment-choices label:nth-of-type(2):has(input:checked) {
  background: #dbeafe !important;
  background-color: #dbeafe !important;
  border-color: #3b82f6 !important;
  box-shadow: inset 0 0 0 999px #dbeafe, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #3b82f6 !important;
  outline: 1px solid #3b82f6 !important;
}

#sentiment-choices label.selected:nth-of-type(3),
#sentiment-choices label:nth-of-type(3):has(input:checked) {
  background: #ede9fe !important;
  background-color: #ede9fe !important;
  border-color: #7c3aed !important;
  box-shadow: inset 0 0 0 999px #ede9fe, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #7c3aed !important;
  outline: 1px solid #7c3aed !important;
}

#sentiment-choices label.selected:nth-of-type(4),
#sentiment-choices label:nth-of-type(4):has(input:checked) {
  background: #ccfbf1 !important;
  background-color: #ccfbf1 !important;
  border-color: #0f766e !important;
  box-shadow: inset 0 0 0 999px #ccfbf1, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #0f766e !important;
  outline: 1px solid #0f766e !important;
}

#sentiment-choices label.selected:nth-of-type(5),
#sentiment-choices label:nth-of-type(5):has(input:checked) {
  background: #ffe4e6 !important;
  background-color: #ffe4e6 !important;
  border-color: #e11d48 !important;
  box-shadow: inset 0 0 0 999px #ffe4e6, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #e11d48 !important;
  outline: 1px solid #e11d48 !important;
}

#sentiment-choices label.selected:nth-of-type(6),
#sentiment-choices label:nth-of-type(6):has(input:checked) {
  background: #dcfce7 !important;
  background-color: #dcfce7 !important;
  border-color: #16a34a !important;
  box-shadow: inset 0 0 0 999px #dcfce7, 0 8px 18px rgba(15, 23, 42, 0.08), 0 0 0 1px #16a34a !important;
  outline: 1px solid #16a34a !important;
}

.thumb-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(124px, 1fr));
}

.thumb-strip {
  display: grid;
  gap: 14px;
  grid-auto-columns: minmax(136px, 168px);
  grid-auto-flow: column;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 6px;
  scroll-snap-type: x proximity;
}

.thumb-strip .thumb-card {
  scroll-snap-align: start;
}

.thumb-card {
  background: var(--story-surface-raised);
  border: 1px solid rgba(216, 204, 188, 0.92);
  border-radius: var(--story-radius-card);
  box-shadow: var(--story-shadow-soft);
  overflow: hidden;
}

.thumb-media {
  aspect-ratio: 4 / 3;
  background: linear-gradient(135deg, #fffdf8, #f3eadf);
  position: relative;
}

.thumb-media img {
  display: block;
  height: 100%;
  object-fit: cover;
  width: 100%;
}

.thumb-fallback {
  align-items: center;
  color: var(--story-ink-muted);
  display: flex;
  font-size: 0.82rem;
  height: 100%;
  justify-content: center;
  padding: 10px;
  text-align: center;
}

.thumb-badge {
  background: rgba(32, 26, 23, 0.82);
  border-radius: 999px;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  left: 10px;
  padding: 6px 9px;
  position: absolute;
  top: 10px;
}

.thumb-meta {
  padding: 10px 12px 12px;
}

.thumb-name {
  color: var(--story-ink);
  font-size: 0.86rem;
  font-weight: 600;
  line-height: 1.35;
  word-break: break-word;
}

.thumb-caption {
  color: var(--story-ink-muted);
  font-size: 0.78rem;
  margin-top: 4px;
}

.status-banner {
  --status-accent: var(--story-support);
  --status-soft: rgba(220, 234, 230, 0.62);
  --status-border: rgba(216, 204, 188, 0.94);
  --status-spinner-track: rgba(63, 111, 106, 0.18);
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.96), rgba(255, 250, 242, 0.92));
  border: 1px solid var(--status-border);
  border-radius: 20px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
  margin-bottom: 18px;
  padding: 14px 16px 14px 18px;
  position: relative;
  overflow: hidden;
}

.status-banner::before {
  background: var(--status-accent);
  border-radius: 999px;
  content: "";
  inset: 10px auto 10px 0;
  position: absolute;
  width: 4px;
}

.status-head,
.icon-heading,
.run-summary-head {
  align-items: flex-start;
  display: flex;
  gap: 12px;
}

.status-copy {
  min-width: 0;
}

.status-icon-wrap {
  align-items: center;
  background: var(--status-soft);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 14px;
  color: var(--status-accent);
  display: inline-flex;
  flex: 0 0 auto;
  height: 40px;
  justify-content: center;
  width: 40px;
}

.status-banner.good {
  --status-accent: var(--story-success);
  --status-soft: rgba(219, 232, 220, 0.86);
  --status-border: rgba(79, 122, 86, 0.26);
  --status-spinner-track: rgba(79, 122, 86, 0.16);
}

.status-banner.caution {
  --status-accent: var(--story-warning);
  --status-soft: rgba(244, 226, 210, 0.88);
  --status-border: rgba(164, 90, 42, 0.24);
  --status-spinner-track: rgba(164, 90, 42, 0.14);
}

.status-banner.processing {
  --status-accent: var(--story-support);
  --status-soft: rgba(220, 234, 230, 0.9);
  --status-border: rgba(63, 111, 106, 0.22);
  --status-spinner-track: rgba(63, 111, 106, 0.16);
}

.status-banner.low-confidence {
  --status-accent: #ba7614;
  --status-soft: rgba(248, 233, 212, 0.9);
  --status-border: rgba(186, 118, 20, 0.24);
  --status-spinner-track: rgba(186, 118, 20, 0.15);
}

.status-banner.error {
  --status-accent: var(--story-danger);
  --status-soft: rgba(242, 221, 217, 0.92);
  --status-border: rgba(154, 63, 53, 0.26);
  --status-spinner-track: rgba(154, 63, 53, 0.15);
}

.status-banner.neutral {
  --status-accent: var(--story-support);
  --status-soft: rgba(220, 234, 230, 0.68);
  --status-border: rgba(216, 204, 188, 0.92);
}

.status-kicker {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin: 0 0 6px;
  text-transform: uppercase;
}

.status-banner .status-kicker {
  color: var(--status-accent);
}

.status-title {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.28rem;
  line-height: 1.15;
  margin: 0;
}

.status-reason {
  color: var(--story-ink-muted);
  font-size: 0.92rem;
  line-height: 1.58;
  margin: 8px 0 0;
}

.ui-icon {
  align-items: center;
  color: currentColor;
  display: inline-flex;
  flex: 0 0 auto;
  height: 18px;
  justify-content: center;
  width: 18px;
}

.status-icon-wrap .ui-icon {
  height: 22px;
  width: 22px;
}

.status-spinner {
  animation: story-spin 0.9s linear infinite;
  border: 3px solid var(--status-spinner-track);
  border-top-color: var(--status-accent);
  border-radius: 999px;
  height: 20px;
  width: 20px;
}

.ui-icon svg {
  display: block;
  height: 100%;
  width: 100%;
}

@keyframes story-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.story-empty-card {
  overflow: hidden;
}

.empty-state-shell {
  align-items: center;
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(120px, 164px) 1fr;
}

.empty-state-shell.compact {
  grid-template-columns: minmax(96px, 132px) 1fr;
}

.empty-state-illustration {
  display: flex;
  justify-content: center;
}

.empty-state-copy h3 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.5rem;
  line-height: 1.15;
  margin: 0 0 10px;
}

.empty-state-shell.compact .empty-state-copy h3 {
  font-size: 1.22rem;
}

.empty-state-eyebrow {
  color: var(--story-support);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.story-mascot {
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.98), rgba(246, 239, 230, 0.96));
  border: 1px solid rgba(216, 204, 188, 0.92);
  border-radius: 26px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  display: inline-flex;
  height: 136px;
  justify-content: center;
  padding: 10px;
  width: 136px;
}

.empty-state-shell.compact .story-mascot,
.run-summary-empty .story-mascot {
  border-radius: 22px;
  height: 104px;
  width: 104px;
}

.story-mascot svg {
  display: block;
  height: 100%;
  width: 100%;
}

.story-mascot.sequence {
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.98), rgba(245, 247, 250, 0.96));
}

.story-mascot.analysis {
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.98), rgba(245, 247, 250, 0.96));
}

.story-mascot.comparison {
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.98), rgba(245, 247, 250, 0.96));
}

.story-card,
.analysis-shell,
.diagnostics-shell,
.correction-status-shell,
.analysis-editor-card,
.analysis-editor-empty {
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 250, 242, 0.96));
  border: 1px solid rgba(216, 204, 188, 0.9);
  border-radius: 22px;
  box-shadow: var(--story-shadow-soft);
  padding: 24px;
}

.story-card.low-confidence {
  border-color: rgba(186, 118, 20, 0.24);
  background: linear-gradient(180deg, rgba(255, 252, 247, 0.98), rgba(249, 240, 229, 0.96));
}

.story-card.error-state {
  border-color: rgba(154, 63, 53, 0.24);
  background: linear-gradient(180deg, rgba(255, 251, 250, 0.98), rgba(247, 234, 231, 0.96));
}

.story-meta {
  color: var(--story-ink-muted);
  font-size: 0.84rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  margin-bottom: 16px;
  text-transform: uppercase;
}

.story-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.run-summary-shell,
.run-detail-shell {
  background: rgba(246, 239, 230, 0.68);
  border: 1px solid rgba(216, 204, 188, 0.88);
  border-radius: 18px;
  margin-bottom: 18px;
  padding: 16px;
}

.run-summary-head,
.run-detail-shell h4 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.02rem;
  margin: 0 0 10px;
}

.run-summary-head .ui-icon,
.icon-heading .ui-icon {
  color: var(--story-support);
  height: 20px;
  margin-top: 1px;
  width: 20px;
}

.run-summary-copy {
  color: var(--story-ink-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.run-summary-empty {
  align-items: center;
  display: flex;
  gap: 16px;
}

.run-highlight-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  margin-top: 14px;
}

.run-highlight {
  background: rgba(255, 253, 249, 0.92);
  border-radius: 14px;
  padding: 10px 12px;
}

.run-highlight-label {
  color: var(--story-ink-muted);
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.run-highlight-value,
.run-table-cell.positive {
  color: var(--story-success);
}

.run-table-cell.negative,
.run-highlight-value.negative {
  color: var(--story-danger);
}

.run-table-cell.neutral,
.run-highlight-value.neutral {
  color: var(--story-ink);
}

.run-comparison-table {
  display: grid;
  gap: 1px;
  grid-template-columns: minmax(130px, 1.1fr) 1fr 1fr 1fr;
  margin-top: 14px;
  width: 100%;
}

.run-table-head,
.run-table-cell {
  background: rgba(255, 253, 249, 0.94);
  padding: 10px 12px;
}

.run-table-head {
  color: var(--story-ink-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.run-table-cell {
  font-size: 0.88rem;
  line-height: 1.45;
}

.run-table-cell.metric {
  color: var(--story-ink);
  font-weight: 600;
}

.story-preview-label {
  color: var(--story-warning);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  text-transform: uppercase;
}

.story-title {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 2rem;
  line-height: 1.15;
  margin: 0 0 16px;
}

.story-body {
  color: var(--story-ink);
  font-size: 1.05rem;
  line-height: 1.85;
  max-width: 58ch;
}

.story-card.low-confidence .story-body {
  color: var(--story-ink-muted);
}

.story-map {
  border-top: 1px solid var(--story-border);
  margin-top: 24px;
  padding-top: 22px;
}

.story-map h3,
.analysis-shell h3,
.diagnostics-shell h3,
.correction-status-shell h3 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.35rem;
  margin: 0 0 14px;
}

.story-map-item {
  border: 1px solid rgba(216, 204, 188, 0.92);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.78);
  margin-bottom: 14px;
  padding: 14px;
}

.story-map-meta {
  color: var(--story-support);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.story-map-sentence {
  color: var(--story-ink);
  font-size: 0.96rem;
  line-height: 1.65;
  margin: 0 0 12px;
}

.story-map-thumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.story-map-thumbs .thumb-card {
  max-width: 124px;
}

.story-map-note {
  color: var(--story-ink-muted);
  font-size: 0.84rem;
  margin: 0;
}

.analysis-grid {
  display: grid;
  gap: 16px;
}

.analysis-editor-card {
  margin-top: 16px;
  padding: 18px;
}

.analysis-editor-header {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(140px, 180px) 1fr;
  margin-bottom: 14px;
}

.analysis-editor-meta h4 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.2rem;
  margin: 0 0 12px;
}

.analysis-card {
  background: rgba(246, 239, 230, 0.7);
  border: 1px solid rgba(216, 204, 188, 0.88);
  border-radius: 18px;
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(140px, 180px) 1fr;
  padding: 16px;
}

.analysis-card .thumb-card {
  margin: 0;
}

.analysis-card h4 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.18rem;
  margin: 0 0 12px;
}

.detail-grid {
  display: grid;
  gap: 10px 18px;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
}

.detail-grid.compact {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.detail-item {
  background: rgba(255, 253, 249, 0.92);
  border-radius: 14px;
  border: 1px solid rgba(216, 204, 188, 0.72);
  padding: 12px;
}

.detail-item.compact {
  padding: 10px;
}

.detail-label {
  color: var(--story-ink-muted);
  display: block;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 7px;
  text-transform: uppercase;
}

.detail-value {
  color: var(--story-ink);
  font-size: 0.9rem;
  line-height: 1.55;
}

.saved-override-note {
  background: rgba(246, 239, 230, 0.7);
  border: 1px solid rgba(216, 204, 188, 0.88);
  border-radius: 14px;
  margin-top: 14px;
  padding: 12px;
}

.saved-override-note.muted {
  background: rgba(246, 239, 230, 0.7);
  border-color: rgba(216, 204, 188, 0.88);
}

.comparison-summary-shell {
  margin: 16px 0 20px;
}

.comparison-shell {
  background: rgba(246, 239, 230, 0.72);
  border: 1px solid rgba(216, 204, 188, 0.88);
  border-radius: 18px;
  margin-top: 16px;
  padding: 16px;
}

.comparison-header {
  margin-bottom: 12px;
}

.comparison-header h5 {
  color: var(--story-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1rem;
  margin: 0 0 6px;
}

.comparison-header p {
  color: var(--story-ink-muted);
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
}

.comparison-table {
  display: grid;
  gap: 1px;
  grid-template-columns: minmax(120px, 1.05fr) minmax(140px, 1fr) minmax(140px, 1fr) 100px;
  width: 100%;
}

.comparison-table-head,
.comparison-cell {
  background: rgba(255, 253, 249, 0.94);
  padding: 10px 12px;
}

.comparison-table-head {
  color: var(--story-ink-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.comparison-cell {
  color: var(--story-ink);
  font-size: 0.88rem;
  line-height: 1.5;
}

.comparison-cell.field {
  font-weight: 600;
}

.comparison-pill {
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 6px 9px;
  text-transform: uppercase;
}

.comparison-pill.changed {
  background: rgba(180, 106, 33, 0.16);
  color: var(--story-warning);
}

.comparison-pill.unchanged {
  background: rgba(47, 125, 79, 0.14);
  color: var(--story-success);
}

.summary-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin-top: 18px;
}

.summary-card {
  background: rgba(246, 239, 230, 0.72);
  border: 1px solid rgba(216, 204, 188, 0.9);
  border-radius: 16px;
  padding: 14px;
}

.summary-card h4 {
  color: var(--story-ink);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin: 0 0 10px;
  text-transform: uppercase;
}

.summary-card p,
.summary-card ul {
  color: var(--story-ink);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
  padding-left: 18px;
}

.summary-card ul {
  margin: 0;
}

.correction-status-shell {
  margin-top: 16px;
}

.analysis-editor-empty {
  margin-top: 16px;
}

.diagnostic-status {
  color: var(--story-ink);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 18px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.chip {
  align-items: center;
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.76rem;
  font-weight: 700;
  gap: 7px;
  letter-spacing: 0.04em;
  padding: 7px 11px;
  text-transform: uppercase;
}

.chip.good {
  background: rgba(79, 122, 86, 0.14);
  color: var(--story-success);
}

.chip.caution {
  background: rgba(164, 90, 42, 0.14);
  color: var(--story-warning);
}

.chip.low-confidence {
  background: rgba(186, 118, 20, 0.14);
  color: #ba7614;
}

.chip.error {
  background: rgba(154, 63, 53, 0.14);
  color: var(--story-danger);
}

.chip.neutral {
  background: rgba(246, 239, 230, 0.82);
  color: var(--story-support);
}

.score-list {
  display: grid;
  gap: 14px;
}

.score-row {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(120px, 160px) 1fr 52px;
  align-items: center;
}

.score-label,
.score-value {
  color: var(--story-ink);
  font-size: 0.9rem;
  font-weight: 600;
}

.score-bar {
  background: rgba(216, 204, 188, 0.78);
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
  position: relative;
}

.score-fill {
  background: linear-gradient(90deg, var(--story-support), var(--story-accent));
  border-radius: 999px;
  height: 100%;
}

.diagnostic-meta,
.notes-list,
.summary-text {
  color: var(--story-ink-muted);
  font-size: 0.92rem;
  line-height: 1.65;
}

.notes-list {
  margin: 12px 0 0;
  padding-left: 18px;
}

.placeholder-copy {
  color: var(--story-ink-muted);
  font-size: 0.95rem;
  line-height: 1.65;
  margin: 0;
}

.empty-state-copy .placeholder-copy {
  max-width: 52ch;
}

#results-tabs button {
  border-radius: 14px !important;
}

#results-tabs {
  margin-top: 4px;
}

#results-tabs [role="tablist"] {
  align-items: stretch;
  background: rgba(242, 233, 220, 0.88) !important;
  border: 1px solid rgba(216, 204, 188, 0.9) !important;
  border-radius: 18px !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
  gap: 8px;
  margin-bottom: 16px;
  padding: 6px !important;
}

#results-tabs [role="tab"] {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  color: var(--story-ink-muted) !important;
  font-weight: 700;
  min-height: 44px;
  padding: 10px 14px !important;
}

#results-tabs [role="tab"]:hover {
  background: rgba(255, 250, 242, 0.74) !important;
  color: var(--story-ink) !important;
}

#results-tabs [role="tab"][aria-selected="true"],
#results-tabs [role="tab"].selected {
  background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 248, 238, 0.96)) !important;
  border: 1px solid rgba(216, 204, 188, 0.92) !important;
  box-shadow: 0 12px 20px rgba(77, 60, 43, 0.1), inset 0 -2px 0 var(--story-accent) !important;
  color: var(--story-ink) !important;
}

#results-tabs [role="tabpanel"] {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 2px 0 0 !important;
}

@media (min-width: 1281px) {
  .workspace-input-column,
  .workspace-result-column {
    align-self: flex-start;
  }

  .input-panel,
  .result-panel {
    max-height: none;
    overflow: visible;
    position: sticky;
    top: 16px;
  }

  .input-panel {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .result-panel {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .result-panel .action-row {
    flex: 0 0 auto;
  }

  #results-tabs {
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    min-height: 0;
  }

  #results-tabs > .tab-wrapper {
    flex: 0 0 auto;
  }

  #results-tabs [role="tabpanel"] {
    min-height: auto;
    overflow: visible;
  }
}

@media (max-width: 1280px) {
  .gradio-container {
    padding: 0 16px 32px;
  }

  .workspace-row {
    flex-wrap: wrap !important;
  }

  .workspace-input-column,
  .workspace-result-column {
    flex: 1 1 100% !important;
    max-width: 100% !important;
    width: 100% !important;
  }

  .empty-state-shell,
  .empty-state-shell.compact,
  .analysis-editor-header,
  .analysis-card,
  .score-row,
  .action-guidance-grid,
  .comparison-table,
  .run-comparison-table {
    grid-template-columns: 1fr;
  }

  .empty-state-illustration,
  .run-summary-empty {
    justify-content: flex-start;
  }

  .run-summary-empty {
    flex-direction: column;
    align-items: flex-start;
  }

  .input-panel,
  .result-panel {
    max-height: none;
    overflow: visible;
    position: static;
  }

  #results-tabs,
  #results-tabs > .tab-wrapper {
    min-width: 0;
    width: 100%;
  }

  #results-tabs [role="tablist"] {
    flex-wrap: wrap !important;
    gap: 8px;
  }

  #results-tabs [role="tab"] {
    flex: 1 1 160px;
    min-width: 0;
  }
}

@media (max-height: 1100px) and (min-width: 1281px) {
  .studio-shell {
    padding: 14px 0 6px;
  }

  .studio-header {
    border-radius: 24px;
    padding: 18px 22px;
  }

  .studio-header h1 {
    font-size: clamp(2rem, 2.8vw, 2.7rem);
  }

  .studio-header p {
    font-size: 0.94rem;
    line-height: 1.5;
    margin-top: 10px;
  }

  .input-panel,
  .result-panel {
    padding: 18px;
  }

  .section-copy {
    margin-bottom: 12px;
  }
}

@media (max-width: 640px) {
  .gradio-container {
    padding: 0 12px 24px;
  }

  .studio-shell {
    padding-top: 16px;
  }

  .studio-header {
    border-radius: 22px;
    padding: 22px 18px;
  }

  .input-panel,
  .result-panel,
  .story-card,
  .analysis-shell,
  .diagnostics-shell,
  .correction-status-shell,
  .analysis-editor-card,
  .analysis-editor-empty {
    padding: 18px;
  }

  .action-row > * {
    flex: 1 1 100%;
  }

  .status-head,
  .action-guidance-item-head,
  .action-guidance-alert {
    align-items: flex-start;
  }

  #results-tabs [role="tab"] {
    flex: 1 1 calc(50% - 4px);
  }
}
"""

APP_HEAD = ""
