"""Validate aggregate survey observations, reconcile them, and publish a summary and deck."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent


def calculate(source, focus):
    buckets = defaultdict(lambda: [0, 0])
    seen = set()
    with source.open(newline="", encoding="utf-8") as stream:
        for line, row in enumerate(csv.DictReader(stream), 2):
            key = tuple(row[k].strip() for k in ("company", "quarter", "topic"))
            yes, total = int(row["favorable"]), int(row["responses"])
            if not all(key) or key in seen or not 0 <= yes <= total or total == 0:
                raise ValueError(f"Invalid or duplicate observation on row {line}")
            seen.add(key)
            counts = buckets[key[2], "focus" if key[0] == focus else "peer"]
            counts[0] += yes
            counts[1] += total
    summary = []
    for topic in sorted({x[0] for x in buckets}):
        a, b = buckets[topic, "focus"], buckets[topic, "peer"]
        if not (a[1] and b[1]):
            raise ValueError(f"Missing focus or comparison observations for {topic}")
        gap = 100 * (a[0] / a[1] - b[0] / b[1])
        summary.append(dict(topic=topic, focus_yes=a[0], focus_total=a[1], peer_yes=b[0], peer_total=b[1], gap_pp=round(gap, 1)))
    if not summary: raise ValueError("No input rows")
    return {"focus": focus, "observations": len(seen), "topics": summary}


def write_deck(result, path):
    deck = Presentation()
    deck.core_properties.author = deck.core_properties.last_modified_by = "Reporting demo"
    slide = deck.slides.add_slide(deck.slide_layouts[5])
    slide.shapes.title.text = "Employee Sentiment Analysis"
    desc = slide.shapes.add_textbox(Inches(.5), Inches(1.4), Inches(9), Inches(.65))
    desc.text = f"{result['focus']} | Favorable answers compared with pooled peers"
    rows = result["topics"]
    table = slide.shapes.add_table(1+len(rows), 4, Inches(.5), Inches(2.3), Inches(9), Inches(3.4)).table
    for j, label in enumerate(["Topic", "Focus answers", "Peer answers", "Gap (pp)"]): table.cell(0,j).text = label
    for i, row in enumerate(rows, 1):
        for j, value in enumerate([row["topic"], f"{row['focus_yes']} / {row['focus_total']}", f"{row['peer_yes']} / {row['peer_total']}", f"{row['gap_pp']:+.1f}"]):
            table.cell(i,j).text = value
    deck.save(path)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, nargs="?", default=ROOT/"examples/responses.csv")
    p.add_argument("--focus", default="Alder Works")
    p.add_argument("--output", type=Path, default=Path("output"))
    args = p.parse_args()
    analysis = calculate(args.source, args.focus)
    args.output.mkdir(parents=True, exist_ok=True)
    write_deck(analysis, args.output/"comparison.pptx")
    (args.output/"summary.json").write_text(json.dumps(analysis, indent=2)+"\n")
    print(f"{analysis['observations']} rows reconciled across {len(analysis['topics'])} topics.")
