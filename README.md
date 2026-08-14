# WoW TCG Card Dataset 👹

An open, flat-file dataset for the World of Warcraft Trading Card Game.

<br>
  
> [!IMPORTANT]
> The structural foundation of this dataset is complete.<br> Every card printing and card oracle has a dedicated file.<br>
> However, much of the actual game properties (rules text, costs, abilities) are incomplete.<br>
> Editors are actively collaborating on this data and welcome community contributions.

<br>

## 📊 Contents

| | |
| --- | --- |
| Card printings | 9,245 |
| Card oracles | 7,743 |
| Sets | 158 |
| Collections | 34 |

<br>

## 🕸️ Structure

During the build process, the compilation script merges the project's individual YAML files into flat, fully-realized JSON objects.

- `data/card/`: **Physical Printings.** Properties specific to an exact card (artist, flavor text, collector number).<br>
  
- `data/oracle/`: **Consistent Properties.** The card's core mechanics that remain identical across all reprints (cost, class, abilities).<br> 
  
- `data/set/`: **Release Data.** Set releases. Cards inherit set properties during build.<br>
  
- `data/collection/`: **Macro-Groupings.** Broader buckets (like blocks or eras) that group multiple sets together.<br>
  
- `data/format/`: **Card Legality.** Standalone rules defining allowed sets and regulations, plus specific card bans and restrictions.<br>
  
- `data/deck/`: **Pre-constructed Lists.** Official product decklists (Starter Decks, Raid Decks) mapping card IDs to quantities — a *specific printing*, not just an oracle.<br>
  
- `schema/`: **Validation Blueprints.** Strict Schemas to automatically validate contributions.<br>
  
- `script/`: **Build Pipeline.** Python utilities that compile the individual YAML files into final distribution formats.<br>
  
- `dist/`: **Distribution Directory.** The final, compiled files. *(Note: This folder is git-ignored. Editors not running the build script locally can instead access these files from the Releases page).*

<br>

### Folder cascade

Cards nest by collection type, collection and set, so the path tells you where a card sits in the release history:

```
data/card/set/01-azeroth/01-heroes-of-azeroth/185-galway-steamwhistle.yml
          └ type └ collection      └ set        └ card
```

Number prefixes come from each record's `index` and order the level chronologically. They are deliberately sparse — supplementary products such as crafting and badge sets sit outside the numbered sequence and carry no prefix. Prefixes are navigation only; **they are not part of any ID**.

Cross-references are written as human-readable names (`set: Heroes of Azeroth`, `collection: Azeroth`) and every ID is derived at build time. See [CONTRIBUTING](CONTRIBUTING.md#-how-ids-work) before adding records.

<br>
  

## 🐍 Scripts
 
- `python script/compile.py`: Validates every source YAML against `schema/`, checks that all cross-references resolve, and writes the joined JSON to `dist/`. **This is the build** — edit YAML, run this, done.<br>
  
- `python script/split.py`: Re-generates `data/card`, `data/oracle`, `data/set`, `data/collection` and `data/deck` from the compiled JSON — the exact inverse of `compile.py`. Useful for bulk structural changes and for normalising formatting. `data/format` is hand-authored and is never touched.<br>

<br>  
  

## 🐝 Community & Contributing

This dataset relies on community contributions to stay accurate and up-to-date. You are invited to contribute if you spot a missing card, a typo in rules text, incorrect set data, etc.
  
*   **[Join Discord](https://chat.cardcarp.com):** Discuss structure and data accuracy.

<br>

## 🪩 Featured Apps

Here are a few projects currently using this dataset in production. (*If you have built an app, simulator, or tool using this data, please share on Discord!*)

*   **[CardCarp](https://cardcarp.com)** - A companion web-app to showcase all cards. 

<br>  
  

## 🍥 Support the Project

If you found this dataset useful and want to help keep it updated, you can support the project below.

*   **[Buy Me a Coffee Page](https://patronage.cardcarp.com)**

  
<br>    
  
## ⚖️ Legal Disclaimer

<sub>This is an independent, community-driven project and is not affiliated with, endorsed by, sponsored by, or connected to any publisher or intellectual property owner.</sub>

<sub>Card data and images are strictly for educational study, historical preservation, and personal, non-commercial use.</sub>

<sub>All trademarks, copyrights, and artwork remain the exclusive property of their respective rights holders.</sub>

<sub>No challenge to any intellectual property rights is intended, nor is there intent to compete with sales or commercial distributions of these intellectual properties.</sub>
