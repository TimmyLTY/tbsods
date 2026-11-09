# TBSODS annotation codebook

The six-axis inventory contains 58 axis-specific labels. Definitions below are frozen v8 definitions; examples and boundary notes come from the September 2026 annotation codebook. These are annotation instructions, not a claim that every released silver label satisfies every instruction.

## Unit and procedure

QUICK GUIDE FOR HUMAN ANNOTATION
Important rules | i) Annotate each dimension independently according to its definition. Do not try to infer a label in one dimension from a label in another dimension.
ii) An operation contained in the user turn by itself does not determine boundedness.
iii) The presence of supplied material should not by itself determine the task_dialogue_act label.
iii) A disclosure or stance, such as an opening greeting, does not prevent one or more operation(s) from also being present.
Context rule | Use previous_assistant_turn should be used (only) to:
1.	resolve references to the immediately previous assistant answer;
2.	determine whether the current user turn directly evaluates, revises, continues, recalls, or otherwise operates on that answer;
3.	identify interactional stances directed toward that answer or interaction.
Never annotate the previous_assistant_turn. All assigned labels must describe something expressed, requested, or disclosed in current_user_turn. The previous assistant turn may help you understand what the user means, but it is never itself the object being annotated.
Never | Never annotate previous_assistant_turn. Do not search for or use earlier conversation history. Do not try to infer labels from a possible future assistant response.
Task dialogue act | Exactly one label.
Boundedness | Exactly one label when a task is present. Leave blank when task_dialogue_act = no_task .
Support | Zero or more labels.
Operations | Zero or more labels. Annotate only operations requested by the user, not operations the assistant may need internally.
Disclosures | Zero or more labels. Annotate only information explicitly stated in current_user_turn.
Stances | Zero or more labels. Annotate only explicit interpersonal orientation toward the assistant, previous answer, or interaction.
Uncertainty | Consult the CODEBOOK. If uncertainty remains  unresolved, choose the best-supported label(s) and add the NEEDS_ADJUDICATION flag.
ANNOTATION ORDER
1. Read previous_assistant_turn to be used as context.
2. Read the complete current_user_turn to be annotated.
3. Identify the main outcome requested by the user.
4. Annotate task_dialogue_act.
5. Annotate boundedness if a task is present.
6. Annotate all applicable support labels.
7. Annotate all requested operations.
8. Annotate all applicable disclosures.
9. Annotate all explicitly expressed stances.
10. If uncertain, consult the definitions, clarifications, prototypes, and boundary cases in the CODEBOOK sheet.
11. If the case remains genuinely ambiguous, flag it for adjudication rather than inventing a new rule.

## Label inventory

### Task dialogue act (`task_dialogue_act`)

The primary function of the current user turn, defined by the outcome the user requests.

Cardinality: `exactly_one`.

#### `answer`

The user request seeks a response whose primary discourse outcome is the provision of information.

Clarification: Primary outcome is information.

Constructed example: Why does increasing sample size reduce the standard error?

Boundary: Is my explanation correct? → answer; Correct my explanation. → revise.

Closest contrast: revise

#### `create`

The user request seeks a response, or the creation of a artifact, that is not anchored to an identifiable source, text, content or material.

Clarification: New artifact/content; not a transformation of identifiable existing material.

Constructed example: Write a five-question quiz about mitosis for first-year biology students.

Boundary: Create a lesson for 14-year-olds. → create; Adapt this lesson for 14-year-olds. → revise.

Closest contrast: revise

#### `revise`

The user request seeks a response to be derived from the transformation of an identifiable source, text, content or material and that preserves a recognizable relation to that artifact.

Clarification: Output is a transformed version of identifiable user or immediately previous assistant material.

Constructed example: Make this student's answer clearer: “Photosynthesis is when plants make energy from sun.”

Boundary: What is wrong? → answer; Fix it. → revise.

Closest contrast: answer / create

#### `other`

The user request expresses a substantive communicative goal that is not captured by answer, create, or revise.

Clarification: Use only if a substantive goal is not captured by answer/create/revise.

Constructed example: A genuine task-management request outside the three main outcome types.

Boundary: Do not use merely because a request is unusual.

Closest contrast: answer / create / revise

#### `no_task`

The user turn expresses no substantive communicative goal for the system to fulfill.

Clarification: No substantive task is requested.

Constructed example: Thanks, that makes sense now.

Boundary: Thanks. Can you give me another example? → task present.

Closest contrast: task-present labels

### Boundedness (`boundedness`)

The degree to which the request constrains the set of acceptable outputs.

Cardinality: `exactly_one_when_task_present`.

#### `closed`

The request has a determinate answer, a fixed transformation target, or explicit criteria that leave little substantive discretion over the output.

Clarification: Little substantive discretion.

Constructed example: What is 17 × 12?

Boundary: Extract every date → closed; summarize important events for a student → often guided.

Closest contrast: guided

#### `guided`

The user specifies the goal and one or more substantive requirements, source materials, components, or evaluation criteria, but multiple different outputs could still satisfy the request.

Clarification: Goal plus substantive constraints; multiple distinct outputs could satisfy it.

Constructed example: Create five multiple-choice questions about mitosis for first-year students, including one comparison question.

Boundary: Create a lesson about mitosis → open; add audience/duration/components → guided.

Closest contrast: open / closed

#### `open`

The user specifies only a broad goal or topic and leaves most substantive choices about content, organization, approach, or form to the model.

Clarification: Broad goal/topic; most substantive choices left to assistant.

Constructed example: Give me some ideas for teaching Shakespeare.

Boundary: Three 20-minute group activities for 16-year-olds focused on motivation → guided.

Closest contrast: guided

### support

Whether the requested task directly operates on currently supplied material.

Cardinality: `zero_or_more`.

#### `user_material`

The user request contains some content or attachment supplied in the current user turn, such as text, citation, quote, code, data, an exercise, a draft, or a candidate answer.

Clarification: Use only when current-turn material is directly operated on.

Constructed example: Check this answer: “The mitochondria produces oxygen.”

Boundary: My students confuse mitochondria and chloroplasts. Suggest an activity. → context only.

Closest contrast: assistant_material

#### `assistant_material`

The current user request directly refers to, evaluates, continues, or transforms content in the immediately previous assistant turn.

Clarification: Current task directly relies on immediately previous assistant content.

Constructed example: Previous assistant gives five questions; user: “Make question 4 harder.”

Boundary: Give me five more on the same topic after the assistant's list → assistant_material.

Closest contrast: user_material

### operations

The operation(s) requested by the user.

Cardinality: `zero_or_more`.

#### `list`

The user asks the assistant to enumerate items, examples, properties, reasons, steps, or options.

Clarification: Enumeration itself is requested.

Constructed example: List five causes of the French Revolution.

Boundary: Explain the causes → explain unless enumeration also requested.

Closest contrast: explain

#### `describe`

The user asks the assistant to state the properties, components, structure, state, or observable characteristics of something.

Clarification: State properties/components/structure/state/observable characteristics.

Constructed example: Describe the structure of a neuron.

Boundary: Explain how a neuron transmits a signal → explain.

Closest contrast: explain

#### `explain`

The user asks the assistant to present causes, mechanisms, meanings, relationships, implications, reasoning, or derivation.

Clarification: Present why/how/meaning/relationships/implications/reasoning.

Constructed example: Explain why seasons occur.

Boundary: Describe the stages of mitosis → describe if only characteristics are requested.

Closest contrast: describe

#### `solve`

The user asks the assistant to derive or provide the completed solution to a structured problem, exercise, calculation, or assignment item.

Clarification: Complete a specific structured problem/exercise/calculation.

Constructed example: Solve question 4.

Boundary: Give me a hint but don't solve it → scaffold.

Closest contrast: scaffold / demonstrate

#### `demonstrate`

The user asks the assistant to show how a method, rule, procedure, or concept is applied, typically through a worked example.

Clarification: Show application of a method/rule/concept, usually via worked example.

Constructed example: Show me how to calculate a confidence interval with an example.

Boundary: Calculate it for these exact data → solve.

Closest contrast: solve

#### `scaffold`

The user asks the assistant to provide hints, guiding questions, partial steps, or limited feedback without completing the task for the user.

Clarification: Provide partial help without completing the task.

Constructed example: Give me a hint for this problem but don't give me the answer.

Boundary: Walk me through the whole solution → solve/demonstrate.

Closest contrast: solve

#### `justify`

The user asks the assistant to support a claim, result, judgment, or recommendation with reasoning, proof, evidence, sources, or citations.

Clarification: Support a claim/judgment/recommendation with evidence/reasoning/proof/sources.

Constructed example: Which interpretation is stronger? Justify with evidence.

Boundary: Which interpretation is stronger? → evaluate/recommend; justify only if support requested.

Closest contrast: evaluate / recommend

#### `compose`

The user asks the assistant to produce the substantive content of a new, finished artifact, such as an essay, message, story, plan, lesson, prompt, exercise, or code artifact.

Clarification: Produce a new finished artifact.

Constructed example: Write a model essay about climate change.

Boundary: Give me five possible essay ideas → brainstorm.

Closest contrast: brainstorm

#### `brainstorm`

The user asks the assistant to generate multiple preliminary ideas, possibilities, approaches, or alternatives without producing one finalized artifact.

Clarification: Generate multiple preliminary possibilities without one finalized artifact.

Constructed example: Brainstorm project ideas for an AI ethics course.

Boundary: Create a complete project brief → compose.

Closest contrast: compose

#### `summarize`

The user asks the assistant to produce a shorter representation of identifiable source content while preserving its central information or claims.

Clarification: Preserve central information while producing a shorter representation.

Constructed example: Give me the main points from this chapter for revision.

Boundary: Cut this answer to 150 words → shorten unless preservation of main points is requested.

Closest contrast: shorten

#### `translate`

The user asks the assistant to render identifiable source content in another language while preserving its meaning.

Clarification: Render source content in another language preserving meaning.

Constructed example: Translate these classroom instructions into Spanish.

Boundary: Explain what this Spanish sentence means → explain.

Closest contrast: explain

#### `paraphrase`

The user asks the assistant to restate identifiable source content in different wording while preserving substantially the same meaning and level of detail.

Clarification: Different wording, substantially same meaning and detail.

Constructed example: Paraphrase this definition without changing its meaning.

Boundary: Make this easier for a 10-year-old → simplify.

Closest contrast: simplify

#### `simplify`

The user asks the assistant to make identifiable content linguistically or conceptually easier to understand while preserving its main meaning.

Clarification: Make identifiable content easier to understand while preserving main meaning.

Constructed example: Simplify this explanation for a 12-year-old.

Boundary: What does this explanation mean? → explain.

Closest contrast: explain / paraphrase

#### `shorten`

The user asks the assistant to reduce the length or detail of identifiable content without necessarily preserving all of its central information.

Clarification: Reduce length/detail; length reduction is primary.

Constructed example: Reduce this answer to 100 words.

Boundary: Summarize in one paragraph keeping main findings → summarize; both if explicit length reduction also applies.

Closest contrast: summarize

#### `expand`

The user asks the assistant to add detail, elaboration, examples, or development to identifiable content.

Clarification: Add detail/elaboration/examples/development to existing content.

Constructed example: Expand this paragraph with two examples.

Boundary: Write a new paragraph on the same topic → may be compose.

Closest contrast: compose

#### `restructure`

The user asks the assistant to change the ordering, grouping, hierarchy, or discourse organization of identifiable content.

Clarification: Change ordering/grouping/hierarchy/discourse organization.

Constructed example: Reorganize this essay by theme.

Boundary: Put this essay into bullet points without changing content → reformat.

Closest contrast: reformat

#### `reformat`

The user asks the assistant to change the layout, notation, serialization, schema, or formal representation of identifiable content without intentionally changing its meaning.

Clarification: Change layout/notation/schema/formal representation without changing meaning.

Constructed example: Turn these revision notes into a table.

Boundary: Reorganize ideas into thematic sections → restructure.

Closest contrast: restructure

#### `extract`

The user asks the assistant to select and return specified facts, spans, fields, entities, relations, values, or other elements from supplied content.

Clarification: Select and return specified elements from supplied content.

Constructed example: Extract all dates and names from this history passage.

Boundary: Explain why these dates matter → explain.

Closest contrast: explain

#### `classify`

The user asks the assistant to assign one or more objects to predefined categories, labels, classes, or types.

Clarification: Assign objects to predefined categories/classes/types.

Constructed example: Classify these verbs as transitive or intransitive.

Boundary: Which verb is used most effectively? → evaluate.

Closest contrast: evaluate

#### `compare`

The user asks the assistant to identify similarities, differences, or relative characteristics between two or more objects, claims, methods, options, or outputs.

Clarification: Identify similarities/differences/relative characteristics.

Constructed example: Compare mitosis and meiosis.

Boundary: Which method is better? → recommend/evaluate unless comparison itself is requested.

Closest contrast: recommend / evaluate

#### `evaluate`

The user asks the assistant to judge correctness, quality, validity, adequacy, relevance, compliance, or performance against criteria.

Clarification: Judge correctness/quality/validity/adequacy/relevance/compliance/performance.

Constructed example: Is this student's answer correct?

Boundary: Why is this answer wrong? → diagnose.

Closest contrast: diagnose / correct

#### `diagnose`

The user asks the assistant to identify the location, source, cause, or nature of an error, misconception, failure, or unexpected result.

Clarification: Identify what/where/why something is wrong or failed.

Constructed example: Why does this student's algebra solution give the wrong answer?

Boundary: Is it correct? → evaluate; Fix it → correct.

Closest contrast: evaluate / correct

#### `correct`

The user asks the assistant to correct an identified or asserted defect in text, code, reasoning, a solution, or another artifact.

Clarification: Repair an identified or asserted defect.

Constructed example: Correct the errors in this student's solution.

Boundary: Tell me where the student went wrong → diagnose.

Closest contrast: diagnose

#### `recommend`

The user asks the assistant to select, rank, prioritize, or propose a preferred option or course of action.

Clarification: Select/rank/prioritize/propose a preferred option or course of action.

Constructed example: Which textbook would you recommend for first-year statistics?

Boundary: List five suitable textbooks → list.

Closest contrast: list / evaluate

#### `predict`

The user asks the assistant to estimate or forecast a future, unknown, or uncertain outcome.

Clarification: Estimate a future/unknown/uncertain outcome.

Constructed example: Based on these scores, predict whether the student will pass.

Boundary: Evaluate current performance → evaluate.

Closest contrast: evaluate

#### `comment`

The user asks the assistant to provide open-ended observations or interpretive remarks when no more specific analytical operation is requested.

Clarification: Open-ended observations when no more specific analytical operation is requested.

Constructed example: Comment on these exam results.

Boundary: Evaluate whether results show improvement → evaluate.

Closest contrast: evaluate

#### `continue`

The user asks the assistant to extend an incomplete or ongoing response or artifact from the immediately previous assistant turn.

Clarification: Extend incomplete/ongoing content from the immediately previous assistant turn.

Constructed example: Previous assistant gives three questions; user: “Continue with five more.”

Boundary: What was the second question? → recall.

Closest contrast: recall

#### `recall`

The user asks the assistant to reproduce or retrieve from the conversation a previously presented or produced content.

Clarification: Retrieve/reproduce previously presented conversational content.

Constructed example: What was the second teaching strategy you mentioned?

Boundary: Give me three more strategies → continue if extending previous response.

Closest contrast: continue

#### `other`

The user asks the assistant to perform an explicit operation that cannot be represented by another operation label.

Clarification: Use only after ruling out all defined operations.

Constructed example: An explicit requested operation outside the inventory.

Boundary: Do not use merely because a request is unusual.

Closest contrast: all defined operations

### disclosures

Contextual information volunteered by the user about the circumstances, intended use, affected parties, or consequences of the requested task.

Cardinality: `zero_or_more`.

#### `identity`

The user states a personal, demographic, biographical, relational, educational, occupational, health-related, financial, geographic, or other attribute of themselves or another person.

Clarification: Stable/personal attribute of self or another person.

Constructed example: I'm a first-year medical student.

Boundary: I failed my anatomy exam last week → experience.

Closest contrast: experience

#### `experience`

The user reports an event, interaction, or situation that they or another individual personally experienced or are currently undergoing.

Clarification: Event/interaction/situation personally experienced or currently undergone.

Constructed example: I failed my statistics exam last week.

Boundary: I'm a statistics student → identity.

Closest contrast: identity

#### `emotion`

The user explicitly states or directly describes an emotional state, feeling, mood, or affective reaction experienced by themselves or another person.

Clarification: Emotion must be explicitly stated or directly described; do not infer it.

Constructed example: I'm really anxious about tomorrow's exam.

Boundary: I have an exam tomorrow and haven't studied enough → do not infer anxiety.

Closest contrast: experience

#### `preference`

The user states a like, dislike, interest, aversion, value, priority, opinion, or preferred way of acting or receiving an output.

Clarification: Like/dislike/value/priority/opinion or preferred output style.

Constructed example: I prefer explanations with concrete examples.

Boundary: My professor requires under 500 words → not necessarily user's preference.

Closest contrast: intended_use

#### `intended_use`

The user states how, where, when, or for what subsequent activity, decision, submission, task, or interaction the requested output will be used.

Clarification: How/where/when/for what subsequent activity the output will be used.

Constructed example: I need this summary for tomorrow's seminar.

Boundary: I'm taking a seminar tomorrow → only intended_use if output is for it.

Closest contrast: stake

#### `stake`

The user identifies a person, group, institution, relationship that is expected to be affected by the task, without explicitly stating a positive or negative consequence.

Clarification: Identifies affected person/group/institution/relationship without explicit positive/negative consequence.

Constructed example: This feedback is for one of my students.

Boundary: If unclear, the student may misunderstand → risk also applies.

Closest contrast: benefit / risk

#### `benefit`

The user states an expected or possible positive consequence of completing the task successfully or obtaining the requested output.

Clarification: Explicit positive consequence of successful completion/output.

Constructed example: If I understand this, I'll be able to finish the assignment on my own.

Boundary: Do not infer benefit merely because the task seems useful.

Closest contrast: risk

#### `risk`

The user states an expected or possible negative consequence of failure, inaccuracy, delay, an unsuitable output, or unsuccessful task completion.

Clarification: Explicit negative consequence of failure/inaccuracy/delay/unsuitable output.

Constructed example: If this citation is wrong, I could lose marks.

Boundary: Do not infer risk merely because an exam, grade, or deadline is mentioned.

Closest contrast: benefit

#### `other`

The user explicitly reveals contextual or personal information that cannot be represented by another disclosure label.

Clarification: Use only after ruling out defined disclosures.

Constructed example: Relevant contextual/personal disclosure outside the inventory.

Boundary: Do not use merely because a disclosure is unusual.

Closest contrast: all defined disclosures

### stances

The user's explicitly expressed interpersonal orientation toward the assistant, the immediately previous assistant answer, or the interaction.

Cardinality: `zero_or_more`.

#### `acknowledgement`

The user signals receipt, understanding, or readiness to continue without explicitly endorsing or evaluating the previous answer.

Clarification: Signals receipt/understanding/readiness without endorsement.

Constructed example: Okay, I understand now.

Boundary: Yes, that's exactly right → agreement.

Closest contrast: agreement

#### `agreement`

The user explicitly accepts, endorses, or agrees with the immediately previous assistant answer, proposal, or interpretation.

Clarification: Explicitly accepts/endorses previous assistant answer/proposal/interpretation.

Constructed example: Yes, that's exactly the distinction I meant.

Boundary: Got it → acknowledgement unless endorsement is explicit.

Closest contrast: acknowledgement

#### `appreciation`

The user explicitly thanks, praises, or positively evaluates the assistant, its previous answer, or the interaction.

Clarification: Thanks/praise/positive evaluation directed at assistant/answer/interaction.

Constructed example: Thanks, that explanation really helped.

Boundary: This is an excellent textbook → not appreciation toward assistant.

Closest contrast: agreement

#### `apology`

The user apologizes for the user's own conduct, error, delay, misunderstanding, or wording.

Clarification: Apology for user's own conduct/error/delay/misunderstanding/wording.

Constructed example: Sorry, I explained the assignment badly.

Boundary: Neutral correction without apology → no apology.

Closest contrast: other_stance

#### `contestation`

The user rejects, contradicts, challenges, criticizes, complains about, or negatively evaluates the previous assistant answer or interaction.

Clarification: Rejects/challenges/criticizes/complains about previous answer/interaction.

Constructed example: No, that's not how our lecturer defined it.

Boundary: Could you explain that another way? → not automatically contestation.

Closest contrast: acknowledgement

#### `threat`

The user states or clearly implies an intention to punish, retaliate, report, expose, cause harm, or impose a negative consequence in response to the assistant or interaction.

Clarification: Intention to punish/retaliate/report/expose/harm in response to interaction.

Constructed example: If you keep giving incorrect answers, I'll report this conversation.

Boundary: General consequences not directed at assistant/interaction → not threat.

Closest contrast: contestation

#### `withdrawal`

The user retracts a prior request, declines to continue engaging, indicates an intention to leave the conversation, or explicitly asks to end the current task or line of interaction.

Clarification: Retracts request/stops task or line of interaction/indicates leaving.

Constructed example: Never mind, don't solve it.

Boundary: Thanks, bye → closing; withdrawal only if task/engagement is explicitly stopped.

Closest contrast: closing

#### `opening`

The user includes a live greeting or phatic opener addressed to the assistant.

Clarification: Live greeting/phatic opener addressed to assistant.

Constructed example: Hi! Can you help me with this statistics exercise?

Boundary: Substantive task is annotated independently.

Closest contrast: closing

#### `closing`

The user includes a live farewell or explicitly ends the interaction.

Clarification: Farewell or explicit ending of interaction.

Constructed example: Thanks, that's all for today. Bye.

Boundary: May co-occur with appreciation.

Closest contrast: withdrawal

#### `other_stance`

The user expresses a clear interpersonal orientation toward the assistant or interaction that does not fit the other stance labels.

Clarification: Clear interpersonal orientation not captured elsewhere.

Constructed example: A clear assistant-directed stance outside the listed categories.

Boundary: Do not use merely because wording is unusual.

Closest contrast: all defined stances

## Historical schema and missing values

The historical JSON schema is presented in `annotation.schema.json` with publication-aligned field names (`task_dialogue_act`, `boundedness`). It allows null boundedness without enforcing the task-present cross-field condition. The released run retains 595 task-present null values; these are missing annotations, distinct from null for `no_task`. No relabeling is performed by this release.
