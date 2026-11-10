# Employee Sentiment Analysis Core Pipeline

This public workflow takes a CSV of aggregate survey counts, checks that every company–quarter–topic appears once, separates the focus company from its peers and generates an editable PowerPoint. It uses a new schema, fictional data and a neutral presentation design.

```sh
python -m pip install -r requirements.txt
python pipeline.py examples/responses.csv --focus "Alder Works" --output output
```

The example reconciles 36 observations across four topics. For growth opportunities, Alder Works has 159 favorable answers out of 288 and pooled peers have 518 out of 756. The gap is −13.3 percentage points. See the [example summary](examples/summary.json) and [editable comparison](examples/comparison.pptx). [Related repositories](https://github.com/search?q=user%3AMRodriguez2010+topic%3Aemployee-sentiment-analysis&type=repositories)
