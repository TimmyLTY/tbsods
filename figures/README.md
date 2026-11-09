# Paper-to-code mapping

Aligned with the Overleaf manuscript downloaded on 9 November 2026: *Characterizing human-LLM delegation: a turn-level annotation framework and resource*.

| Paper content | Released files | Computation |
| --- | --- | --- |
| Framework overview, Fig. 1 | `framework/delegation_pipeline.pdf` | Manuscript illustration; includes bilateral annotation and the human-validation zoom |
| Constructed annotation example, Fig. 2 | `framework/user_turn_annotation.pdf` | Manuscript illustration |
| Delegation distributions and group differences, Fig. 3 | `delegation_combined.png` | `descriptive/analyze.py`, `descriptive/plot.py` |
| Operation–feedback associations, Fig. 4 | `feedback_cooccurrence.png`, `feedback_contestation.png`, `feedback_appreciation.png` | `feedback/run_feedback.py`, `feedback/fit_all_overall.py`, `feedback/plot.py` |
| Boundedness–feedback associations, Fig. 5 | `boundedness_cooccurrence.png`, `boundedness_overall_contestation.png`, `boundedness_overall_appreciation.png` | `boundedness/run_boundedness.py`, `boundedness/plot.py` |
| Repeated use, Fig. 6 | `repeated_use_stances.png` | `longitudinal/run_analysis.py`, `longitudinal/plot.py` |
| Additional combined positive-feedback outcome | `feedback_positive_feedback.png` | Same feedback scripts; this panel is currently commented out in the paper |

Run all analysis scripts through `python scripts/reproduce.py --results-dir results` from the repository root. The scripts share `resource_io.py`, which derives strict turn adjacency, retained-turn ranks and operation counts from the compact release.

The descriptive figure displays eight selected contrasts across GPT-4/GPT-3.5 and China/United States. The two panels have different horizontal scales. Statistical calculations retain the original four-comparison, 232-test BH family. Regional and language-environment comparisons are retained in computed tables for that correction, while their discussion and display have been removed from the current paper. The historical region variable also remains in feedback regression controls.

The framework PDFs are the current manuscript exports, supplied as illustrations. The numerical scripts generate PNG versions of the analysis figures; they do not rebuild the framework drawings, the LaTeX page layout or the paper's human-validation tables.
