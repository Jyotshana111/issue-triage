"""Public, no-card demo of the same model used by the local full-stack app."""

import html

import joblib
import streamlit as st
from scipy.sparse import csr_matrix, hstack

from semantic_search import PREFIX, SemanticIssueSearch, issue_text


EXAMPLES = {
    "Bug report": (
        "read_csv crashes when the file has an empty header",
        "Reading a CSV file with an empty header raises an error instead of returning a DataFrame.",
    ),
    "Documentation": (
        "Add an example for reading compressed CSV files",
        "The read_csv documentation should include a short example using a gzip compressed file.",
    ),
    "Enhancement": (
        "Support a custom date format in read_csv",
        "Allow users to pass a date format when parsing a column in read_csv.",
    ),
}


@st.cache_resource(show_spinner=False)
def load_analysis():
    return joblib.load("issue_model.joblib"), SemanticIssueSearch()


def analyze(title, body):
    classifier, search = load_analysis()
    words = classifier["vectorizer"].transform(
        [f"{PREFIX.sub('', title)} {body[:1500]}"]
    )
    meaning = search.model.encode(
        issue_text(title, body), normalize_embeddings=True
    )
    features = hstack([words, csr_matrix(meaning.reshape(1, -1))]).tocsr()
    label = str(classifier["classifier"].predict(features)[0])
    return label, search.search(title, body)


def set_example(name):
    st.session_state.issue_title, st.session_state.issue_body = EXAMPLES[name]
    st.session_state.pop("result", None)


st.set_page_config(
    page_title="Issue Triage Assistant · Live Demo",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 3rem; }
      h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -.03em; }
      .brand { font: 800 1.25rem 'Plus Jakarta Sans', sans-serif; color: #29264e; margin-bottom: 1.1rem; }
      .brand span { color: #7666e7; }
      .hero { padding: 2.6rem 3rem; border-radius: 22px; color: white;
              background: radial-gradient(circle at 90% 5%, #ad9df5, transparent 30%),
                          linear-gradient(115deg, #302d7d, #5a4fbe 56%, #8b75e5);
              box-shadow: 0 16px 32px #4f4ba526; }
      .hero .eyebrow { color: #e2dcff; font-size: .72rem; font-weight: 700; letter-spacing: .13em; }
      .hero h1 { color: white; margin: .7rem 0 .55rem; font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.16; }
      .hero p { color: #e4e0ff; font-size: 1.02rem; max-width: 530px; margin: 0; }
      .section-kicker { color: #7769d9; font-size: .72rem; font-weight: 800; letter-spacing: .12em; margin-top: 2rem; }
      .section-note { color: #858ca4; margin: -.5rem 0 1.1rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] > div { border-color: #e8e9f2; border-radius: 16px; }
      div.stButton > button[kind="primary"] { border-radius: 9px; background: #6556dc; border: none; font-weight: 700; }
      div.stButton > button { border-radius: 9px; font-weight: 700; }
      .result-label { display: inline-block; color: #5c4fc7; background: #efedff; border-radius: 8px;
                      font: 800 1.2rem 'Plus Jakarta Sans', sans-serif; padding: .6rem .9rem; }
      .muted { color: #858ca4; font-size: .9rem; }
      .issue-rank { color: #8d80dd; font-weight: 800; font-size: .83rem; }
      .steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
      .step-card { padding: 1.25rem; background: white; border: 1px solid #e8e9f2;
                   border-radius: 16px; min-height: 155px; }
      .step-card span { color: #7668df; font-size: .75rem; font-weight: 800; }
      .step-card h3 { margin: .6rem 0 .35rem; font-size: 1rem; }
      .step-card p { color: #858ca4; font-size: .87rem; line-height: 1.5; margin: 0; }
      .footnote { color: #9299ac; font-size: .8rem; margin-top: 1.5rem; }
      @media (max-width: 640px) { .hero { padding: 2rem 1.35rem; } .block-container { padding-top: 1rem; }
                                  .steps-grid { grid-template-columns: 1fr; } .step-card { min-height: auto; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand">✦ triage<span>.ai</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><div class="eyebrow">AI-POWERED ISSUE TRIAGE · LIVE DEMO</div>'
    '<h1>From issue report<br>to clear next steps.</h1>'
    '<p>Suggest a label and discover related pandas issues in one thoughtful workflow.</p></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-kicker">01 / ANALYZE</div>', unsafe_allow_html=True)
st.header("Analyze an issue")
st.markdown(
    '<p class="section-note">Paste an issue or choose an example. The model uses the title and description.</p>',
    unsafe_allow_html=True,
)

form_column, example_column = st.columns([1.8, 1], gap="large")
with form_column:
    with st.container(border=True):
        st.subheader("Issue details")
        with st.form("issue_form"):
            title = st.text_input("Issue title", key="issue_title", max_chars=300,
                                  placeholder="e.g. read_csv crashes on an empty header")
            body = st.text_area("Description · optional", key="issue_body", height=145,
                                placeholder="What happened? What did you expect instead?")
            submitted = st.form_submit_button("✦  Analyze issue", type="primary",
                                              use_container_width=True)

with example_column:
    with st.container(border=True):
        st.subheader("Try an example")
        st.caption("Start with a realistic pandas issue")
        for name in EXAMPLES:
            st.button(name, key=f"example_{name}", use_container_width=True,
                      on_click=set_example, args=(name,))
        st.caption("A maintainer makes the final triage decision.")

if submitted:
    if not title.strip():
        st.warning("Enter an issue title first.")
    else:
        try:
            with st.spinner("Classifying and finding related issues. First use may download the model…"):
                label, matches = analyze(title.strip(), body.strip())
            st.session_state.result = (title.strip(), label, matches)
        except Exception as error:
            st.error(f"Analysis could not complete: {error}")

if "result" in st.session_state:
    analyzed_title, label, matches = st.session_state.result
    st.markdown('<div class="section-kicker">02 / RESULTS</div>', unsafe_allow_html=True)
    st.header("Your analysis")
    st.markdown('<p class="section-note">A starting point for faster, more informed triage.</p>',
                unsafe_allow_html=True)

    label_column, count_column = st.columns(2, gap="large")
    with label_column, st.container(border=True):
        st.caption("SUGGESTED LABEL")
        st.markdown(f'<div class="result-label">{html.escape(label)}</div>', unsafe_allow_html=True)
        st.caption("Predicted from the issue title and description. Review before applying.")
    with count_column, st.container(border=True):
        st.caption("RELATED ISSUES")
        st.metric("Results from the indexed pandas collection", len(matches))

    st.subheader("Related issues")
    st.caption("Open each report to decide whether it describes the same problem.")
    for index, issue in enumerate(matches, start=1):
        with st.container(border=True):
            rank, details, score = st.columns([0.45, 6, 1], vertical_alignment="center")
            with rank:
                st.markdown(f'<span class="issue-rank">{index:02d}</span>', unsafe_allow_html=True)
            with details:
                st.link_button(issue["title"], issue["url"], use_container_width=True)
            with score:
                st.caption(f'Score {issue["score"]:.3f}')

    st.info("Similarity scores measure text closeness, not the probability of a duplicate. Review each linked issue.")
    summary = "\n".join([
        f"Issue: {analyzed_title}",
        f"Suggested label: {label}",
        "", "Related issues:",
        *(f'- {issue["title"]} ({issue["url"]})' for issue in matches),
    ])
    st.download_button("Download summary", summary, file_name="issue-triage-summary.txt")

st.markdown('<div class="section-kicker">BEHIND THE SCENES</div>', unsafe_allow_html=True)
st.header("How it works")
st.markdown(
    '<p class="section-note">The same Python model powers this public demo and the local full-stack app.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="steps-grid">'
    '<div class="step-card"><span>01</span><h3>Describe</h3>'
    '<p>Enter a title and optional context for a GitHub issue.</p></div>'
    '<div class="step-card"><span>02</span><h3>Classify</h3>'
    '<p>A trained model suggests Bug, Docs, or Enhancement.</p></div>'
    '<div class="step-card"><span>03</span><h3>Compare</h3>'
    '<p>Sentence embeddings rank related issues for human review.</p></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="footnote">Powered by TF-IDF, sentence embeddings and logistic regression. '
    '<a href="https://github.com/Jyotshana111/issue-triage" target="_blank">View the full React · Java · Python project on GitHub ↗</a></div>',
    unsafe_allow_html=True,
)
