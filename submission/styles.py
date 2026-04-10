from __future__ import annotations

APP_CSS = """
:root {
  --story-bg: #f3f5f7;
  --story-surface: #ffffff;
  --story-surface-strong: #f5f7fa;
  --story-ink: #050505;
  --story-ink-muted: #222222;
  --story-border: #d9dee5;
  --story-accent: #e16f46;
  --story-accent-soft: #ffe1d4;
  --story-support: #1f6f78;
  --story-support-soft: #edf4f6;
  --story-success: #2f7d4f;
  --story-warning: #b46a21;
  --story-danger: #b84747;
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
  background: radial-gradient(circle at top, #ffffff 0%, var(--story-bg) 58%, #e9edf2 100%);
  color-scheme: light;
}

html,
body {
  min-height: 100%;
  overflow-x: hidden;
}

body,
.gradio-container {
  --background-fill-primary: #f3f5f7 !important;
  --background-fill-secondary: #ffffff !important;
  --block-background-fill: #ffffff !important;
  --block-border-color: #d9dee5 !important;
  --body-text-color: #050505 !important;
  --body-text-color-subdued: #222222 !important;
  --input-background-fill: #ffffff !important;
  --button-secondary-background-fill: #ffffff !important;
  --button-secondary-text-color: #050505 !important;
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

body.dark .gradio-container .wrap,
body.dark .gradio-container .form,
body.dark .gradio-container .block,
body.dark .gradio-container .gr-box,
body.dark .gradio-container .gr-group,
body.dark .gradio-container .gr-panel,
body.dark .gradio-container [data-testid="file-upload"],
body.dark .gradio-container [data-testid="block-label"],
body.dark .gradio-container [role="tablist"],
body.dark .gradio-container [role="tab"],
body.dark .gradio-container [role="tabpanel"] {
  background: var(--story-surface) !important;
  border-color: var(--story-border) !important;
  color: var(--story-ink) !important;
}

body.dark .gradio-container input,
body.dark .gradio-container textarea,
body.dark .gradio-container select,
body.dark .gradio-container button {
  color: var(--story-ink) !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container select {
  background: var(--story-surface) !important;
  border-color: var(--story-border) !important;
  color: var(--story-ink) !important;
}

.gradio-container .main,
.gradio-container .main.fillable.app,
.gradio-container .wrap,
.gradio-container .contain {
  background: transparent !important;
  color: var(--story-ink) !important;
}

.gradio-container .form,
.gradio-container .block,
.gradio-container .gr-box,
.gradio-container .gr-group,
.gradio-container .gr-panel,
.gradio-container [data-testid="block-label"],
.gradio-container [role="tablist"],
.gradio-container [role="tab"],
.gradio-container [role="tabpanel"] {
  background: var(--story-surface) !important;
  border-color: var(--story-border) !important;
  color: var(--story-ink) !important;
}

.gradio-container [data-testid="file-upload"] {
  background: var(--story-surface-strong) !important;
  border-color: var(--story-border) !important;
  color: var(--story-ink) !important;
}

.gradio-container [data-testid="file-upload"] *,
.gradio-container [role="tab"] *,
.gradio-container [role="tabpanel"] *,
.gradio-container label,
.gradio-container .form *,
.gradio-container .block * {
  color: var(--story-ink) !important;
}

.gradio-container button {
  background: var(--story-surface) !important;
  border-color: var(--story-border) !important;
  color: var(--story-ink) !important;
}

.gradio-container button:disabled,
.gradio-container button[disabled] {
  background: var(--story-surface-strong) !important;
  color: var(--story-ink-muted) !important;
  opacity: 1 !important;
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
  padding: 24px 0 8px;
}

.studio-header {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(217, 222, 229, 0.95);
  border-radius: 28px;
  padding: 28px 30px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
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
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(217, 222, 229, 0.98);
  border-radius: 24px;
  min-width: 0;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.input-panel,
.result-panel {
  padding: 22px;
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
  background: rgba(5, 5, 5, 0.9);
  border-radius: 999px;
  box-shadow: 0 16px 34px rgba(5, 5, 5, 0.18);
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
  display: flex;
  margin: 4px 0 18px;
  flex-wrap: wrap;
  gap: 10px;
}

.action-row button {
  border-radius: 12px !important;
}

.action-guidance-shell {
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid rgba(217, 222, 229, 0.95);
  border-radius: 16px;
  margin: 0 0 18px;
  padding: 14px 16px;
}

.action-guidance-shell.running {
  background: rgba(245, 247, 250, 0.96);
  border-color: rgba(217, 222, 229, 0.95);
}

.action-guidance-title {
  color: var(--story-ink);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.action-guidance-copy,
.action-guidance-list {
  color: var(--story-ink-muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.action-guidance-copy {
  margin: 0;
}

.action-guidance-list {
  margin: 10px 0 0;
  padding-left: 18px;
}

.action-guidance-list li + li {
  margin-top: 6px;
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

#generate-button {
  background: linear-gradient(135deg, #ffe8df, #ffd0bd) !important;
  border: 1px solid #e16f46 !important;
  border-radius: 14px;
  box-shadow: 0 14px 24px rgba(225, 111, 70, 0.24);
  color: var(--story-ink) !important;
  font-weight: 700;
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
  background: var(--story-surface);
  border: 1px solid var(--story-border);
  border-radius: 18px;
  overflow: hidden;
}

.thumb-media {
  aspect-ratio: 4 / 3;
  background: linear-gradient(135deg, #ffffff, #f1f3f6);
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
  background: rgba(5, 5, 5, 0.84);
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
  border-radius: 20px;
  margin-bottom: 16px;
  padding: 18px 20px;
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
  background: rgba(255, 255, 255, 0.94);
  border-radius: 16px;
  display: inline-flex;
  flex: 0 0 auto;
  height: 48px;
  justify-content: center;
  width: 48px;
}

.status-banner.good {
  background: rgba(247, 249, 252, 0.98);
  border: 1px solid rgba(47, 125, 79, 0.34);
}

.status-banner.caution {
  background: rgba(247, 249, 252, 0.98);
  border: 1px solid rgba(180, 106, 33, 0.32);
}

.status-banner.processing {
  background: rgba(247, 249, 252, 0.98);
  border: 1px solid rgba(31, 111, 120, 0.28);
}

.status-banner.low-confidence,
.status-banner.error {
  background: rgba(247, 249, 252, 0.98);
  border: 1px solid rgba(184, 71, 71, 0.3);
}

.status-kicker {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.status-banner.good .status-kicker {
  color: var(--story-success);
}

.status-banner.caution .status-kicker {
  color: var(--story-warning);
}

.status-banner.processing .status-kicker {
  color: var(--story-support);
}

.status-banner.low-confidence .status-kicker,
.status-banner.error .status-kicker {
  color: var(--story-danger);
}

.status-title {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.45rem;
  line-height: 1.15;
  margin: 0;
}

.status-reason {
  color: var(--story-ink-muted);
  font-size: 0.96rem;
  line-height: 1.6;
  margin: 10px 0 0;
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
  height: 24px;
  width: 24px;
}

.status-spinner {
  animation: story-spin 0.9s linear infinite;
  border: 3px solid rgba(31, 111, 120, 0.18);
  border-top-color: var(--story-support);
  border-radius: 999px;
  height: 24px;
  width: 24px;
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
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.98), rgba(245, 247, 250, 0.96));
  border: 1px solid rgba(217, 222, 229, 0.95);
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
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(217, 222, 229, 0.95);
  border-radius: 22px;
  padding: 24px;
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
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid rgba(217, 222, 229, 0.95);
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
  background: rgba(255, 255, 255, 0.98);
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
  background: rgba(255, 255, 255, 0.98);
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
  border: 1px solid var(--story-border);
  border-radius: 18px;
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
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid rgba(217, 222, 229, 0.95);
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
  background: rgba(255, 255, 255, 0.98);
  border-radius: 14px;
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
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid rgba(217, 222, 229, 0.95);
  border-radius: 14px;
  margin-top: 14px;
  padding: 12px;
}

.saved-override-note.muted {
  background: rgba(245, 247, 250, 0.96);
  border-color: rgba(217, 222, 229, 0.95);
}

.comparison-summary-shell {
  margin: 16px 0 20px;
}

.comparison-shell {
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid rgba(217, 222, 229, 0.95);
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
  background: rgba(255, 255, 255, 0.98);
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
  background: rgba(245, 247, 250, 0.96);
  border: 1px solid var(--story-border);
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
  background: rgba(47, 125, 79, 0.14);
  color: var(--story-success);
}

.chip.caution {
  background: rgba(180, 106, 33, 0.14);
  color: var(--story-warning);
}

.chip.low-confidence,
.chip.error {
  background: rgba(184, 71, 71, 0.14);
  color: var(--story-danger);
}

.chip.neutral {
  background: rgba(245, 247, 250, 0.96);
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
  background: rgba(217, 222, 229, 0.9);
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
  border-radius: 999px !important;
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

  #results-tabs [role="tab"] {
    flex: 1 1 calc(50% - 4px);
  }
}
"""

APP_HEAD = ""
