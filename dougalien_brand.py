"""Dougalien Systems look for the Streamlit apps.

Colors come from the Dougalien Systems logo (sand, slate, rust) and match
dougalien.com. The base palette lives in .streamlit/config.toml; this module
adds the logo, a strata stripe under the header and a few light CSS touches,
and darkens the light gray Streamlit uses for captions, widget labels and
chart text. It only changes appearance, never app behavior.

Usage, right after st.set_page_config(...):

    from dougalien_brand import apply_branding
    apply_branding()

Headings: call app_header(title, tagline) once, at the top of the front page, and page_header(title, intro)
at the top of every other page or tab, so each one says what is on it without repeating the app title.
"""

import base64
import html
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ASSETS / "dougalien_systems_logo.png"
MARK = ASSETS / "dougalien_mark.png"
MARK_SVG = ASSETS / "dougalien_mark.svg"
SITE_URL = "https://www.dougalien.com"
SITE_NAME = "www.dougalien.com"

PAPER = "#F4F4F1"
SHEET = "#FFFFFF"
INK = "#1B1E20"
MUTED = "#586770"
RULE = "#D6DBDA"
CAPTION = "#2F3A40"
AXIS_LINE = "#586770"
SLATE = "#3E5C6B"
RUST = "#B4532A"
SAND = "#D6B27C"
SAND_TINT = "#EFE8DA"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&display=swap');

/* Header bar: paper background with the logo's strata as a stripe along the bottom */
[data-testid="stHeader"] {{
  background: {PAPER};
}}
[data-testid="stHeader"]::after {{
  content: "";
  position: absolute; left: 0; right: 0; bottom: 0; height: 5px;
  background: linear-gradient(90deg,
    {SAND} 0 22%, {SLATE} 22% 34%, {SAND} 34% 62%,
    {RUST} 62% 70%, {SAND} 70% 88%, {SLATE} 88% 100%);
  pointer-events: none;
}}

/* Headings in the dougalien.com display face */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: "Familjen Grotesk", "Helvetica Neue", Arial, sans-serif;
  letter-spacing: -0.01em;
}}
.stApp h1 {{ color: {INK}; font-weight: 700; }}
.stApp h2, .stApp h3 {{ color: {SLATE}; font-weight: 600; }}

/* Sidebar: soft sand panel with a rule on the edge */
[data-testid="stSidebar"] {{
  background: {SAND_TINT};
  border-right: 1px solid {RULE};
}}

/* Links, metrics, expanders, tabs, captions */
.stApp a {{ color: {SLATE}; }}
.stApp a:hover {{ color: {RUST}; }}
[data-testid="stMetricValue"] {{ color: {SLATE}; }}
[data-testid="stExpander"] details {{
  border-color: {RULE};
  background: {SHEET};
}}
.stTabs [data-baseweb="tab-list"] {{ border-bottom: 1px solid {RULE}; }}
.stTabs [aria-selected="true"] {{ color: {SLATE}; }}
/* Captions, widget labels and help text: dark instead of Streamlit's faded gray */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {{ color: {CAPTION} !important; opacity: 1 !important; }}
[data-testid="stWidgetLabel"] p {{ color: {INK} !important; }}
[data-testid="stMetricLabel"] p {{ color: {INK} !important; }}
.stApp small {{ color: {CAPTION}; }}

/* Buttons: slate fill for primary (from the theme), rust edge on hover for the rest */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  border-radius: 4px;
  font-weight: 600;
}}
.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button[kind="secondary"]:hover {{
  border-color: {RUST};
  color: {RUST};
}}

/* Logo links home to dougalien.com: show that it is a link on hover and keyboard focus */
[data-testid="stLogoLink"] {{ border-radius: 4px; }}
[data-testid="stLogoLink"]:hover img {{ opacity: 0.8; }}
[data-testid="stLogoLink"]:focus-visible {{ outline: 3px solid {SLATE}; outline-offset: 3px; }}
/* The script that labels the logo link takes no space on the page */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > script:only-child) {{ display: none; }}

/* Front-page label: the strata D mark beside "Dougalien Systems", above the app title */
.dg-label {{
  display: inline-flex; align-items: center; gap: 0.45rem;
  font-family: "Familjen Grotesk", "Helvetica Neue", Arial, sans-serif;
  font-weight: 600; font-size: 0.95rem; letter-spacing: 0.02em;
  color: {SLATE} !important; text-decoration: none !important;
}}
.dg-label img {{ width: 1.6rem; height: 1.6rem; }}
.dg-label:hover {{ color: {RUST} !important; }}
/* The label and the website address sit on one line, with a sand dot between them */
.dg-labelrow {{
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.2rem 0.6rem; margin-bottom: -0.6rem;
}}
.dg-dot {{ color: {SAND}; font-weight: 700; }}
.dg-site {{
  font-family: "Familjen Grotesk", "Helvetica Neue", Arial, sans-serif;
  font-weight: 500; font-size: 0.95rem; letter-spacing: 0.02em;
  color: {SLATE} !important; text-decoration: underline; text-decoration-color: {SAND};
  text-underline-offset: 0.2em;
}}
.dg-site:hover {{ color: {RUST} !important; text-decoration-color: {RUST}; }}
/* One plain line under the app title or a page heading */
.dg-tagline {{ font-size: 1.15rem; color: {INK}; margin: -0.4rem 0 1.2rem 0; max-width: 52rem; }}
.dg-intro {{ font-size: 1.02rem; color: {CAPTION}; margin: -0.4rem 0 1rem 0; max-width: 52rem; }}

/* Quotes pick up the rust accent */
.stApp blockquote {{ border-left: 3px solid {RUST}; }}
</style>
"""


# Streamlit names the logo link only "Logo"; give it a real name for screen readers and a hover tooltip
_HOME_LABEL = "Dougalien Systems home page (opens in a new tab)"
_HOME_JS = f"""
<script>
(function () {{
  if (window.__dougalienHome) return;
  window.__dougalienHome = true;
  function label() {{
    document.querySelectorAll('a[data-testid="stLogoLink"]').forEach(function (a) {{
      if (a.getAttribute("aria-label") === "{_HOME_LABEL}") return;
      a.setAttribute("aria-label", "{_HOME_LABEL}");
      a.setAttribute("title", "Visit dougalien.com");
      var img = a.querySelector("img");
      if (img) img.setAttribute("alt", "Dougalien Systems");
    }});
  }}
  label();
  new MutationObserver(label).observe(document.body, {{ childList: true, subtree: true }});
}})();
</script>
"""


def _logo():
    if not hasattr(st, "logo") or not LOGO.exists():
        return
    # No icon_image, so apps without a sidebar show the full lockup in the header too
    try:
        st.logo(str(LOGO), size="large", link=SITE_URL)
    except TypeError:  # Streamlit without the size option
        st.logo(str(LOGO), link=SITE_URL)


def _dark_plotly(fig):
    """Dark axis, legend and title text on a Plotly figure, where the app hasn't set a color itself."""
    try:
        if fig.layout.font.color is None:
            fig.layout.font.color = INK
        fig.for_each_xaxis(_dark_axis)
        fig.for_each_yaxis(_dark_axis)
        layout = fig.layout
        if layout.legend.font.color is None:
            layout.legend.font.color = INK
        if layout.title.font.color is None:
            layout.title.font.color = INK
        for ann in layout.annotations or ():
            if ann.font.color is None:
                ann.font.color = INK
    except Exception:  # never let styling break a chart
        pass
    return fig


def _dark_axis(axis):
    if axis.color is not None:  # the app colored this axis on purpose (e.g. to match a series)
        return
    if axis.tickfont.color is None:
        axis.tickfont.color = INK
    if axis.title.font.color is None:
        axis.title.font.color = INK
    if axis.linecolor is None:
        axis.linecolor = AXIS_LINE


def _dark_altair(chart):
    """Dark axis, legend and header text on an Altair chart."""
    try:
        return (
            chart.configure_axis(labelColor=INK, titleColor=INK, labelFontSize=12, titleFontSize=13,
                                 domainColor=AXIS_LINE, tickColor=AXIS_LINE)
            .configure_legend(labelColor=INK, titleColor=INK, labelFontSize=12, titleFontSize=13)
            .configure_header(labelColor=INK, titleColor=INK)
            .configure_title(color=INK)
        )
    except Exception:  # layered/faceted charts that can't take a config: leave as is
        return chart


def _patch_charts():
    """Route st.plotly_chart and st.altair_chart (also on columns and containers) through the dark styling."""
    from streamlit.delta_generator import DeltaGenerator

    if getattr(DeltaGenerator, "_dougalien_dark", False):
        return

    plotly_chart, altair_chart = DeltaGenerator.plotly_chart, DeltaGenerator.altair_chart

    def dark_plotly_chart(self, figure_or_data, *args, **kwargs):
        if hasattr(figure_or_data, "update_layout"):
            figure_or_data = _dark_plotly(figure_or_data)
        return plotly_chart(self, figure_or_data, *args, **kwargs)

    def dark_altair_chart(self, altair_chart_obj, *args, **kwargs):
        return altair_chart(self, _dark_altair(altair_chart_obj), *args, **kwargs)

    DeltaGenerator.plotly_chart = dark_plotly_chart
    DeltaGenerator.altair_chart = dark_altair_chart
    DeltaGenerator._dougalien_dark = True


def _bind_charts():
    # st.plotly_chart is bound to the main area when Streamlit is imported, so rebind it to the patched methods
    from streamlit.delta_generator import DeltaGenerator

    main = getattr(st.plotly_chart, "__self__", None)
    if main is not None:
        st.plotly_chart = DeltaGenerator.plotly_chart.__get__(main)
        st.altair_chart = DeltaGenerator.altair_chart.__get__(main)


def apply_branding():
    """Add the Dougalien Systems logo and brand styling to the current page."""
    try:
        _patch_charts()
        _bind_charts()
    except Exception:  # older or newer Streamlit internals: skip the chart styling
        pass
    _logo()
    if hasattr(st, "html"):
        st.html(_CSS)
        try:
            st.html(_HOME_JS, unsafe_allow_javascript=True)
        except TypeError:  # Streamlit without script support in st.html: the logo still links home
            pass
    else:
        st.markdown(_CSS, unsafe_allow_html=True)


def _mark_src():
    """The D mark as an inline image, so the label needs no extra request."""
    if MARK_SVG.exists():
        return "data:image/svg+xml;base64," + base64.b64encode(MARK_SVG.read_bytes()).decode()
    if MARK.exists():
        return "data:image/png;base64," + base64.b64encode(MARK.read_bytes()).decode()
    return None


def app_header(title, tagline):
    """Front page only: the Dougalien Systems label with the D mark, the app title, and one plain line on what the app does."""
    src = _mark_src()
    mark = f'<img src="{src}" alt="">' if src else ""
    st.markdown(f'<div class="dg-labelrow"><a class="dg-label" href="{SITE_URL}" target="_blank" rel="noopener" '
                f'title="Visit dougalien.com">{mark}Dougalien Systems</a><span class="dg-dot" aria-hidden="true">·</span>'
                f'<a class="dg-site" href="{SITE_URL}" target="_blank" rel="noopener">{SITE_NAME}</a></div>',
                unsafe_allow_html=True)
    st.title(title, anchor=False)
    st.markdown(f'<p class="dg-tagline">{html.escape(tagline)}</p>', unsafe_allow_html=True)


def page_header(title, intro=None, level=1):
    """Heading for one page or tab: says what is on it, with an optional short intro. Leave out the app title here.

    level=1 for a page of its own; level=2 for a section that sits under app_header on the front page.
    """
    (st.title if level == 1 else st.header)(title, anchor=False)
    if intro:
        st.markdown(f'<p class="dg-intro">{html.escape(intro)}</p>', unsafe_allow_html=True)


def page_icon(default="🪨"):
    """Logo mark for st.set_page_config(page_icon=...), or the emoji if the file is missing."""
    return str(MARK) if MARK.exists() else default
