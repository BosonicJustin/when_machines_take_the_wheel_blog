# When Machines Take the Wheel

The article site: a single self-contained `index.html` (all figures, images, styles, and chart code embedded — no build step, no external dependencies).

- **Authors:** Justinas Zaliaduonis, Joris Zilinskis, Fabian Hildesheim, Joel Hainzl, Gediminas Pazera
- **Benchmark source:** the [catalog-integrity environment](https://github.com/BosonicJustin/e_commerce_env) (`ecommerce_env` repo) — all numbers in the article come from `benchmarks/` there.

## Preview locally

```bash
python3 -m http.server 8791
# open http://localhost:8791/index.html
```

Light theme is the default; the "theme" button in the top bar toggles dark.

## Editing notes

- Everything lives in `index.html`: CSS at the top, article HTML in the middle, chart-drawing JavaScript at the bottom (`<script>` block). Custom charts (divide, plateau, prompt tax, reward payoffs, bankruptcy, break-even, training curve) are plain data arrays in that script — edit numbers there.
- The five matplotlib figures (GRPO diagram, model ladder, mechanism, cost scatter) are base64-embedded SVGs generated from `ecommerce_env/benchmarks/figures/`. To update one, regenerate it there and re-embed.
- Writing rules live in `.claude/skills/article-writing/SKILL.md` and load automatically in Claude Code sessions inside this repo. Highlights: no em dashes, no numbers in headlines, scope every claim, zero self-praise adjectives.

## Before publication (open items)

- [x] Footnote 1: Ramp revenue-divide data — sourced to Eric Glyman's X post
- [ ] Footnote 2: Uber budget / Microsoft licenses — link pending, verify
- [ ] Footnote 4: Ramp spreadsheet agent — single-source, verify primary
- [x] Training curves are real W&B evals (raw exports in data/)
- [ ] Confirm the $50k build-cost assumption in the break-even chart
- [ ] Replace the mailto CTA with a booking link (two places: top bar + CTA panel)
- [ ] Decide "Catalogue" (Part IV heading) vs "catalog" (used everywhere else)
- [ ] Co-author red-team pass: hunt the claim you'd attack in the comments
