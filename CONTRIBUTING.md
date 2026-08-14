# Contributing

Thank you for helping maintain this data!

Before jumping in, please review these community resources:

*   **[Join Discord](https://chat.cardcarp.com):** Discuss structure and data accuracy.

## 🌭 Local Setup

Before submitting a pull-request, please test your changes locally to ensure they compile correctly.

1. Clone repository.
2. Install required Python dependencies: `pip install .`
3. Run the compile script to verify your YAML syntax and schema compliance: `python script/compile.py`

## 🪲 Automated Validation

Every pull-request is automatically validated against the schema via GitHub Actions. If the pipeline fails, your pull-request cannot be merged. You can view the exact line causing the error by clicking "Details" on the failed GitHub-Action check.

The build also checks that every cross-reference resolves. A card pointing at an oracle that does not exist, or a format banning a card by an ID nothing uses, fails the build and names the offender. Schema validation cannot catch this, because it only ever sees one file at a time.

<br>

## 🔑 How IDs Work

**Never write an ID into a YAML file.** Every ID is derived from the record's own properties at build time, and cross-references are written as human-readable names.

| Record | ID is derived from | Example |
| --- | --- | --- |
| Collection | `name` | `Azeroth` → `azeroth` |
| Set | `name` | `Heroes of Azeroth` → `heroes-of-azeroth` |
| Card | `set` + `index` | `Heroes of Azeroth` + `185` → `heroes-of-azeroth-185` |
| Oracle | `name` + `origin` | `Galway Steamwhistle` + `heroes-of-azeroth-185` → `galway-steamwhistle-heroes-of-azeroth-185` |
| Deck | `collection` + `name` | `2013` + `Alliance Rogue` → `2013-alliance-rogue` |

So a card references its set as `set: Heroes of Azeroth`, not `set: heroes-of-azeroth`. The build kebab-cases it for you.

**`oracle` is the one reference written in kebab-case**, because an oracle has no single human name that identifies it — `oracle: galway-steamwhistle-heroes-of-azeroth-185`.

Filenames exist purely so editors can find things. Renaming a file changes nothing about the data. If two records derive the same ID the build **fails and names both files**, rather than silently overwriting one.

### `origin` on oracles

Names are not unique — six different cards are called "Deathwing the Destroyer". `origin` anchors an oracle to the printing it first appeared in (`aspects-002`), so the ID stays unique. It is anchored to the *earliest* printing so that adding reprints never changes an existing oracle's ID.

### Oracle IDs vs card IDs

The two shapes answer different questions. An **oracle** identifies a set of mechanics shared by every printing of a card — what it does. A **card** identifies one specific printing — its artist, rarity, set and collector number.

Card IDs are not merely internal plumbing: deck lists reference them, because a decklist has to name the printing that shipped in the box rather than just the mechanics.

<br>

## 📇 `index`

`index` is the printed collector number on a card, and the ordering label on a set or collection.

On **cards** it is required and zero-padded (`'001'`, `'185'`). On **sets and collections it is deliberately sparse.** Main-line releases are numbered `01`, `02`, `03`; their companion products take a letter suffix (`01a` for the tokens belonging to set `01`); and supplementary products — crafting sets, badge sets, holiday promos — are left unnumbered on purpose.

An unnumbered set is not missing data. Its folder simply carries no prefix:

```
data/card/set/01-azeroth/
    01-heroes-of-azeroth/
    01a-heroes-of-azeroth-tokens/
    02-through-the-dark-portal/
    azeroth-badges-of-justice/     <- outside the numbered sequence
    azeroth-crafting/
```

<br>

## 🧬 Curation Decisions

Where a judgement call was made about the data, it is recorded here. **Please do not "correct" these back without raising it on Discord first.**

### Punctuation in names

381 oracle names once carried an underscore where an apostrophe, quote, colon or question mark belonged — an artefact of an earlier import. These have been restored:

```
A_dal                      ->  A'dal
_A Plague upon Thee!_      ->  "A Plague upon Thee!"
Darkmoon Card_ Hurricane   ->  Darkmoon Card: Hurricane
Why Do We Fight_           ->  Why Do We Fight?
_Backstab_ Bindo Gearbomb  ->  "Backstab" Bindo Gearbomb
```

A residue remains: some names have a bare `-s` where a possessive apostrophe belongs (`A'dals Signet` should likely be `A'dal's Signet`). Apostrophes are stripped when deriving IDs, so fixing these does **not** change any ID and can be done at any time.

### Format legality

A card is legal in a format if **either** its set is allowed **or** its regulation is — not both. Regulation marks are a newer mechanic, so older cards qualify by set alone and newer ones by mark alone. An empty `set_allow` or `regulation_allow` means the format does not admit cards by that route at all.

Note that `regulation` is currently unpopulated on every oracle, so any format gating purely on regulation matches nothing.

### Deck `collection`

A deck's `collection` field is a folder grouping (`2013`, `raid`, `champion`), **not** a reference to `data/collection`. The build deliberately does not check it.

<br>

## 🎴 What Counts as a Set

A set is a group of cards sharing a set-mark and its own numbering sequence — not a retail product. Tokens, crafting cards and badges ship alongside a main set but number independently, so each is its own set here, linked to the same collection.
