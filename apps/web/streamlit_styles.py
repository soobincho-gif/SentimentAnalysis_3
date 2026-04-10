from __future__ import annotations

STREAMLIT_CSS = """
<style>
  :root {
    --story-bg: #f6f1e8;
    --story-surface: #fffaf2;
    --story-surface-strong: #f2e9dc;
    --story-surface-raised: #fffdf9;
    --story-ink: #201a17;
    --story-ink-muted: #635851;
    --story-border: #d8ccbc;
    --story-accent: #c55c38;
    --story-accent-soft: #f7d8c8;
    --story-support: #3f6f6a;
    --story-support-soft: #dceae6;
    --story-success: #4f7a56;
    --story-warning: #a45a2a;
    --story-danger: #9a3f35;
  }

  .stApp {
    background:
      radial-gradient(circle at top, rgba(255, 253, 249, 0.98), rgba(246, 241, 232, 0.98) 52%, rgba(236, 226, 211, 1) 100%);
    color: var(--story-ink);
  }

  #MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
  }

  [data-testid="stSidebar"] {
    background: rgba(255, 250, 242, 0.92);
    border-right: 1px solid rgba(216, 204, 188, 0.85);
  }

  [data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
  }

  [data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 4rem;
  }

  .hero-shell,
  .panel-card,
  .story-card,
  .status-card,
  .placeholder-card,
  .note-card,
  .story-map-card,
  .observation-card {
    background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 250, 242, 0.96));
    border: 1px solid rgba(216, 204, 188, 0.92);
    border-radius: 24px;
    box-shadow: 0 18px 42px rgba(77, 60, 43, 0.08);
  }

  .hero-shell {
    margin-bottom: 1.25rem;
    padding: 1.75rem 1.8rem;
  }

  .hero-kicker,
  .section-kicker,
  .status-kicker,
  .story-meta,
  .label-chip {
    color: var(--story-ink-muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin: 0;
    text-transform: uppercase;
  }

  .hero-title,
  .story-title,
  .status-title {
    color: var(--story-ink);
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.08;
    margin: 0;
  }

  .hero-title {
    font-size: clamp(2.2rem, 4vw, 3.4rem);
    margin-top: 0.35rem;
  }

  .hero-copy,
  .status-copy,
  .story-body,
  .body-copy {
    color: var(--story-ink-muted);
    font-size: 1rem;
    line-height: 1.7;
  }

  .repo-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .repo-links a,
  .link-pill {
    background: rgba(255, 250, 242, 0.92);
    border: 1px solid rgba(216, 204, 188, 0.9);
    border-radius: 999px;
    color: var(--story-ink);
    display: inline-flex;
    font-size: 0.92rem;
    font-weight: 600;
    gap: 0.4rem;
    padding: 0.55rem 0.95rem;
    text-decoration: none;
  }

  .panel-card {
    padding: 1.2rem 1.25rem 1.1rem;
  }

  .panel-title {
    color: var(--story-ink);
    font-size: 1.2rem;
    font-weight: 700;
    margin: 0 0 0.4rem;
  }

  .panel-copy {
    color: var(--story-ink-muted);
    margin: 0 0 1rem;
  }

  .status-card {
    border-left: 6px solid var(--story-support);
    margin-bottom: 1rem;
    padding: 1rem 1.1rem;
  }

  .status-card.good { border-left-color: var(--story-success); }
  .status-card.caution { border-left-color: var(--story-warning); }
  .status-card.low-confidence { border-left-color: #ba7614; }
  .status-card.error { border-left-color: var(--story-danger); }

  .status-title {
    font-size: 1.35rem;
    margin-top: 0.25rem;
  }

  .story-card {
    margin-bottom: 1rem;
    padding: 1.3rem 1.35rem;
  }

  .story-title {
    font-size: 1.75rem;
    margin-top: 0.4rem;
  }

  .story-body {
    color: var(--story-ink);
    margin-top: 1rem;
    white-space: pre-wrap;
  }

  .placeholder-card,
  .note-card,
  .story-map-card,
  .observation-card {
    margin-bottom: 0.9rem;
    padding: 1rem 1.05rem;
  }

  .label-chip {
    color: var(--story-support);
    margin-bottom: 0.4rem;
  }

  .note-card ul,
  .story-map-card ul,
  .observation-card ul {
    margin: 0.3rem 0 0 1.1rem;
  }

  .warning-chip,
  .state-chip {
    border-radius: 999px;
    display: inline-flex;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.35rem 0.6rem;
    text-transform: uppercase;
  }

  .state-chip.good { background: rgba(79, 122, 86, 0.14); color: var(--story-success); }
  .state-chip.caution { background: rgba(164, 90, 42, 0.14); color: var(--story-warning); }
  .state-chip.low-confidence { background: rgba(186, 118, 20, 0.14); color: #ba7614; }
  .state-chip.error { background: rgba(154, 63, 53, 0.14); color: var(--story-danger); }

  .metric-caption {
    color: var(--story-ink-muted);
    font-size: 0.85rem;
    margin-top: -0.25rem;
  }

  .streamlit-image-frame {
    background: rgba(255, 253, 249, 0.85);
    border: 1px solid rgba(216, 204, 188, 0.82);
    border-radius: 22px;
    box-shadow: 0 12px 26px rgba(77, 60, 43, 0.06);
    padding: 0.55rem;
  }

  .streamlit-image-frame img {
    border-radius: 16px;
  }

  .small-note {
    color: var(--story-ink-muted);
    font-size: 0.9rem;
  }
</style>
"""
