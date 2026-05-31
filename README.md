# WoW TCG Card Dataset 👹

An open, flat-file dataset for the World of Warcraft Trading Card Game.

<br>
  
> [!IMPORTANT]
> The structural foundation of this dataset is complete.<br> Every card printing and card oracle has a dedicated file.<br>
> However, much of the actual game properties (rules text, costs, abilities) are incomplete.<br>
> Editors are actively collaborating on this data and welcome community contributions.

<br>

## 🕸️ Structure

During the build process, the compilation script merges the project's individual YAML files into flat, fully-realized JSON objects.

- `data/card/`: **Physical Printings.** Properties specific to an exact card (artist, flavor text, set number).<br>
  
- `data/oracle/`: **Consistent Properties.** The card's core mechanics that remains identical across all reprints (cost, class, abilities).<br> 
  
- `data/set/`: **Release Data.** Set releases. Cards inherit set properties during build.<br>
  
- `data/collection/`: **Macro-Groupings.** Broader buckets (like blocks or eras) that group multiple sets together.<br>
  
- `data/format/`: **Card Legality.** Standalone rules defining allowed sets, and specific card bans/restrictions.<br>
  
- `data/deck/`: **Pre-constructed Lists.** Official product decklists (Starter Decks, Raid Decks) mapping card IDs to quantities.<br>
  
- `schema/`: **Validation Blueprints.** Strict Schemas to automatically validate contributions.<br>
  
- `script/`: **Build Pipeline.** Python utilities that compile the individual YAML files into final distribution formats.<br>
  
- `dist/`: **Distribution Directory.** The final, compiled files. *(Note: This folder is git-ignored. Editors not running the build script locally can instead access these files from the Releases page).*

<br>
  

## 🐍 Scripts
 
- `python script/compile.py`: Validates all source YAMLs and generates the joined JSON in `dist/`.<br>
  
- `python script/split.py`: Re-generates the modular YAML structure from the joined JSON.<br>

- `python script/manifest.py`: (Extra) Joins all JSON and performs example manipulations.<br>

- `python script/list-set.py`: (Extra) Compiles a list of all sets.<br>

- `python script/list-set.py`: (Extra) Compiles a list of all array-type property values.

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

Please consider donating if this dataset saved you hours of manual data entry.

*   **[Chum Fund](https://chum.cardcarp.com/)**

  
<br>    
  
## ⚖️ Legal Disclaimer

<sub>This is an independent, community-driven project and is not affiliated with, endorsed by, sponsored by, or connected to any publisher or intellectual property owner.</sub>

<sub>Card data and images are strictly for educational study, historical preservation, and personal, non-commercial use.</sub>

<sub>All trademarks, copyrights, and artwork remain the exclusive property of their respective rights holders.</sub>

<sub>No challenge to any intellectual property rights is intended, nor is there intent to compete with sales or commercial distributions of these intellectual properties.</sub>
