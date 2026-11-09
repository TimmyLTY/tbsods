# License

Copyright © 2026 TBSODS contributors. The following component-specific licenses apply to this repository.

| Component | License | Scope |
| --- | --- | --- |
| Original Python code in `scripts/` and `figures/`, including docstrings | MIT | Reuse, modification and redistribution, including commercial use, with copyright and license notices retained |
| Original documentation, taxonomy, codebook, prompts, schemas, configuration and original illustrations | CC BY 4.0 | Original contributions; requires attribution, a license link and indication of changes |
| Newly contributed annotation labels and selection decisions | CC BY 4.0 | Authors' rights in the added annotation layer; does not relicense WildChat messages or metadata |
| The assembled WildChat-derived database and source-derived components | ODC-BY 1.0 | Preserve upstream attribution and notices; the assembled database is released under ODC-BY 1.0 |
| Unicode CLDR-derived country mapping | Existing Unicode terms | Preserve the existing license text and attribution |

The data files contain multiple layers. Source messages, assistant context, locators and source-derived metadata retain their upstream provenance. The six-axis and education labels are the added annotation layer. The text-free files in `data/frozen/` also contain source locators and the existing source-proxy encoding; not every field is newly authored.

ODC-BY governs database rights and does not itself license all rights in each individual item of content. The CC BY grant is limited to original contributions in which the licensors have rights. Neither MIT nor CC BY replaces the WildChat or Unicode terms. These are component-specific licenses, not a choice of any single license for the whole repository.

The source WildChat-1M data is distributed upstream under the [Open Data Commons Attribution License v1.0 (ODC-BY)](https://opendatacommons.org/licenses/by/1-0/). This repository preserves its attribution and does not claim ownership over the source messages or supersede upstream terms. Consult the [versioned data card](https://huggingface.co/datasets/allenai/WildChat-1M/blob/7d6490e462285cf85d91eabea0f9a954fbddcd1f/README.md).

Unicode CLDR 44 data is third-party material with its own copyright and license, preserved in `figures/descriptive/UNICODE-LICENSE.txt`. See `NOTICE.md`.

## License texts

- [MIT](LICENSES/MIT.txt)
- [CC BY 4.0](LICENSES/CC-BY-4.0.txt)
- [ODC-BY 1.0](LICENSES/ODC-By-1.0.txt)
- [Unicode](figures/descriptive/UNICODE-LICENSE.txt)
