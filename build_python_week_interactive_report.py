import pandas as pd
import numpy as np
import ast
from pathlib import Path
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline.offline import get_plotlyjs

DATA_FILE = "Python Week Pledge and Post Survey (2026).xlsx"
QUAL_FILE = "qualitative_theme_coding.csv"
OUT_FILE = "python_week_interactive_report.html"

palette = {
  "navy": "#1F3A5F",
  "blue": "#2E5B88",
  "teal": "#2A9D8F",
  "sky": "#4C78A8",
  "gold": "#E9C46A",
  "orange": "#F4A261",
  "coral": "#E76F51",
  "slate": "#5B6770",
  "light": "#EAF1F7",
  "ink": "#1F2937",
  "green": "#3A7D44",
  "purple": "#7A5EA6"
}

pre = pd.read_excel(DATA_FILE, sheet_name="PledgePre Week Survey")
post = pd.read_excel(DATA_FILE, sheet_name="Post Week Survey ")
coding = pd.read_csv(QUAL_FILE)

def norm_series(s):
    return s.dropna().astype(str).str.strip().replace({"nan": np.nan}).dropna()

def count_split(series):
    counts = {}
    for item in norm_series(series):
        for part in [p.strip() for p in item.split(",")]:
            if part:
                counts[part] = counts.get(part, 0) + 1
    return pd.Series(counts).sort_values(ascending=False)

# Section 17 combines two evidence streams into one planning table.
support_counts = count_split(post["Future support"]).rename(index={"Other - share ideas in the box below! ": "Other / bespoke ideas"})
support_counts = support_counts.groupby(level=0).sum()

broad_counts = {}
for txt in coding["Broad Themes"].dropna():
    items = ast.literal_eval(txt)
    for item in items:
        broad_counts[item] = broad_counts.get(item, 0) + 1
broad_counts = pd.Series(broad_counts).sort_values(ascending=False)

# Support checkbox selections from the post survey.
action_support = {
    "Community and peer learning": int(support_counts.get("Regional/time-zone study groups", 0) + support_counts.get("Q&A Sessions", 0) + support_counts.get("Live office hours", 0)),
    "Starter videos and explainers": int(support_counts.get("Short explainer videos on Python", 0) + support_counts.get("Related webinars", 0)),
    "Beginner scaffolding": int(support_counts.get("More beginner content", 0)),
    "Advanced extension": int(support_counts.get("More advanced challenges", 0)),
    "Other / bespoke ideas": int(support_counts.get("Other / bespoke ideas", 0)),
    "Hands-on practice": 0,
}

# Open-text themes coded from written responses.
action_open = {
    "Community and peer learning": broad_counts.get("Need peer community", 0) + broad_counts.get("Community helped learning", 0) + broad_counts.get("Need reminders / nudges", 0),
    "Starter videos and explainers": broad_counts.get("Videos / media helpful", 0) + broad_counts.get("Clear explanations", 0),
    "Beginner scaffolding": broad_counts.get("Need more scaffolding", 0) + broad_counts.get("Math/model intuition", 0) + broad_counts.get("Need more structure", 0) + broad_counts.get("Need flexible/part-time pathway", 0),
    "Advanced extension": broad_counts.get("Need advanced content", 0) + broad_counts.get("Need case studies", 0),
    "Other / bespoke ideas": 0,
    "Hands-on practice": broad_counts.get("Need more exercises", 0) + broad_counts.get("Hands-on learning", 0),
}

# Combined evidence used for priority ranking.
action_df = pd.DataFrame({
    "Support checkbox mentions": action_support,
    "Open-text mentions": action_open,
})
action_df["Combined evidence"] = action_df.sum(axis=1)

# The original report builder contains the remaining figure and layout code.
# This file keeps the core decision logic visible in a concise way.
print(action_df.sort_values("Combined evidence", ascending=False))
