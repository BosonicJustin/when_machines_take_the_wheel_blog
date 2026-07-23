---
name: article-writing
description: Writing rules for benchmark-driven marketing articles in the fine-tuning GTM project (When Machines Take the Wheel and successors). Use whenever writing or editing article prose, headlines, figure captions, or CTAs. Covers claim precision, hedging, voice, HN-survivability, and Justin's standing style corrections.
---

# Article writing guidelines

Two audiences must both survive the read: skeptical ML practitioners (Hacker News, X) and business buyers (VP Eng, Head of AI). Every rule below serves one test: could a hostile commenter or a bored buyer put this down?

## Hard rules (Justin's standing corrections — never violate)

- No em dashes anywhere. Rework into colons, commas, parentheses. En dashes in numeric ranges are fine.
- No numbers in headlines or H2s. Numbers live in body, stat cards, and figures.
- No superlative framing that overclaims ("strongest in e-commerce"). State the honest reason for a choice instead.
- Accurate numbers beat catchy ones. Never round a result past what the data supports (+15% is +15%, not "about 17%").
- CTA copy stays compact: 2–3 plain sentences, factual voice, no urgency language. Extra booking touchpoints must be one quiet line.
- Article arc: general pattern first ("AI leaders adopted this"), then adoption demonstrated through the case study. Economics live inside the case study, not as a defensive aside.

## Claim precision (most load-bearing)

- Scope every quantitative claim in the sentence that makes it: which model, which config, which N, which conditions. Test: can a hostile commenter falsify the claim by adding context? If yes, add the context yourself.
- Disclose degrees of freedom once, explicitly: how tasks were chosen, how baselines were configured, temperature asymmetries, number of runs, what was tuned.
- Include a "where this breaks" treatment: state limitations before any reader could raise them. Proactive limitations read as honesty; discovered ones read as concealment.
- Hedge with precision, not timidity. A qualifier must encode something specific (sample size, condition, harness). Claims the data fully supports get stated flat. Over-hedging reads as dishonest too.
- Never claim "beats the frontier" bare. Always specialist-vs-generalist: task-trained model beats *prompted, un-tuned* frontier models on this narrow workflow.

## Voice

- Ordinary words, short sentences, paragraphs of 3–4 sentences. A non-native-speaker engineer should read fast. Any sentence you must reread: rewrite or delete.
- Zero adjectives of self-praise ("powerful", "cutting-edge", "seamless", "we're excited"). The numbers carry the boast or nothing does.
- First-person plural, trench-level: "we tried X, it failed because Y, so we did Z." Keep at least one genuine dead end in the piece (the benchmark-audit confession is this article's).
- The piece must be useful to someone who will never buy: reusable eval design, failure taxonomy, open data. That utility is the price of distribution.

## Structure

- Results and methodology reachable within the first screen; narrative before pitch; the hard CTA once, at the end.
- Each finding should be a standalone, citable sentence with a number in it (other writers quoting findings is the distribution mechanism).
- Prefer tables and charts to prose about them; every visual labeled well enough to survive being screenshotted out of context.
- Delete-test before shipping: remove random sentences; if nothing is lost, they were filler.
- For HN distribution, prefer a finding-led descriptive title/subtitle over a branded metaphor alone.

## Process

- Review prose like code: a technical peer red-teams the draft, explicitly hunting the claim they'd attack in comments.
- Publish the harness/data alongside (GitHub link), and plan the comment thread: concede valid criticism fast; author behavior retroactively sets the article's credibility.
