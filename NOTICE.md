# Third-party attribution

## WildChat

This resource includes conversations and metadata derived from **WildChat: 1M ChatGPT Interaction Logs in the Wild**, by Wenting Zhao, Xiang Ren, Jack Hessel, Claire Cardie, Yejin Choi and Yuntian Deng (ICLR 2024).

- [Paper](https://openreview.net/forum?id=Bl8u7ZRlbM)
- [Dataset, pinned revision](https://huggingface.co/datasets/allenai/WildChat-1M/tree/7d6490e462285cf85d91eabea0f9a954fbddcd1f)
- [Upstream data card](https://huggingface.co/datasets/allenai/WildChat-1M/blob/7d6490e462285cf85d91eabea0f9a954fbddcd1f/README.md)
- [ODC-BY v1.0](https://opendatacommons.org/licenses/by/1-0/)

Changes: selection of the education-related analysis cohort; projection to user-turn records with their preceding assistant context; addition of TBSODS annotations and documented analysis fields; preservation of compact source locators and conversation-level metadata. The original text and frozen labels are not rewritten during packaging. WildChat's authors do not endorse this derived taxonomy or its analyses.

## Unicode CLDR

The fixed country mapping in `figures/descriptive/country_mapping.csv` is derived from Unicode CLDR **release-44**, Copyright © 1991–2023 Unicode, Inc.

- [CLDR English territory names](https://github.com/unicode-org/cldr/blob/release-44/common/main/en.xml)
- [CLDR supplemental data](https://github.com/unicode-org/cldr/blob/release-44/common/supplemental/supplementalData.xml)
- License: `figures/descriptive/UNICODE-LICENSE.txt`
