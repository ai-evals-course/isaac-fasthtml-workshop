Make sure to follow ALL requirements

Summary
We need a lightweight, keyboard-driven annotation tool that integrates with Phoenix’s REST API to fetch candidate documents, record relevance judgments from subject matter experts (Brian and Ahmed) and send back to Phoenix into our golden data set. The tool must support two-phase annotation (initial independent rating by two reviewers, followed by a final joint resolution phase) and push the final labeled data back into Phoenix’s golden dataset. This will streamline the labeling workflow and expand our “golden dataset” for search relevance experiments.

User Story Statement

As a search relevance reviewer,
I want an efficient web-based annotation interface that pulls candidate documents via the Phoenix REST API and lets me mark them as “Relevant” or “Not Relevant” with simple keyboard shortcuts,
so that we can quickly build and maintain a high-quality Golden Dataset for evaluating SmartSearch.

Acceptance Criteria

Candidate Retrieval from Phoenix

The tool pulls candidate entries (document text or snippets) via Phoenix’s REST API.

Each candidate entry includes:

ankihub_id (unique identifier),

Document content or title/snippet,

similarity_score (used for ranking).

The tool sets their initial status to READY FOR INITIAL ANNOTATION.

Independent Initial Annotation Phase

Two distinct reviewers can use the tool independently (no advanced authentication needed; each reviewer just enters their name/ID when using the tool).

Scrollable UI displaying candidate entries in descending order of similarity_score (most relevant at top).

Keyboard shortcuts for labeling:

Press 1 = Mark Relevant

Press 0 = Mark Not Relevant

Annotations auto-save in real-time; a “Submit” button is also provided to confirm the reviewer’s completion.

After both reviewers finish this step:

Candidate entries’ status automatically updates to READY FOR FINAL ANNOTATION.

Final Annotation & Disagreement Resolution

Entries with disagreements (e.g., one reviewer marked 1, the other marked 0) appear at the top of the final annotation queue, visually highlighted (e.g. red background).

The UI shows both reviewers’ initial ratings side-by-side.

The reviewers collaboratively select a Final Rating (1 or 0) and add a short text feedback note (both can edit a shared field).

Changes auto-save in real-time (both see updates). A “Save Final Annotation” button is present to confirm.

When saved, each entry’s status updates to FINAL ANNOTATION COMPLETE.

Data Push to Phoenix

Once an entry is FINAL ANNOTATION COMPLETE, the tool pushes the final relevance label (final_rating) and feedback text back to Phoenix’s REST API to update the golden dataset.

Confirm that each record is properly created/updated in Phoenix with:

ankihub_id

final_rating (1 or 0)

feedback_text (if provided)

Final status or relevant metadata

UI/UX Requirements

Minimal design but clear for quick scanning.

Ranking by similarity_score so the user sees the highest-likelihood matches first.

Keyboard-driven interactions to speed up labeling.

No advanced authentication needed beyond reviewer name input. (Out of scope: user account system.)

Out of Scope

No advanced analytics or dashboards.

No manual addition of new items to the dataset.

No complex user role/permission management.

Implementation Considerations

Prefer a fast, lightweight framework (e.g. FastHTML) for quick setup.

REST integration with Phoenix must handle:

Retrieving candidates & statuses,

Updating statuses/annotations,

Pushing final labeled data.

Real-time saving & synchronization may leverage a small backend or serverless function.

Make sure to handle conflict resolution (i.e., if both reviewers try to edit the same entry). Likely the final annotation phase is collaborative, so just ensure last save wins or real-time merges.

Success Metrics

Speed of labeling: Reduce the annotation cycle from weeks to days/hours.

No missing data: All entries get final annotation or resolution.

Smooth integration: Confirm final annotations are correctly reflected in Phoenix’s golden dataset (e.g. via a small sample verification).

Tasks (Suggested Breakdown)

Backend Setup

Integrate with Phoenix REST API to fetch candidate entries (status READY FOR INITIAL ANNOTATION) and update statuses/annotations.

Implement or configure a minimal server or serverless endpoint for real-time save.

Handle a final push to Phoenix for final_rating and feedback.

UI/Front End

Initial Annotation Screen: Display candidate entries in descending similarity_score order; attach keyboard shortcuts (1, 0) for relevant/not relevant.

Reviewer Identification: Simple way to record reviewer’s ID or name.

Final Annotation Screen: Highlight disagreements, show side-by-side initial annotations, let users set final rating + short feedback.

Auto-save & Submit: Real-time local save, plus a final “Submit” or “Save Final Annotation” button.

Visual indicator or filter for items with disagreements.

Status Management

On completion of each reviewer’s initial pass, automatically set item status to READY FOR FINAL ANNOTATION.

On final annotation, set status to FINAL ANNOTATION COMPLETE.

Ensure statuses are in sync with Phoenix and do not regress to earlier states.

Testing & Validation

Unit Tests: For API integration (fetch, update), local state management, status transitions.

End-to-End Tests: Two mock reviewers annotate sample data, then finalize it. Verify final results appear correctly in Phoenix.

Keyboard Shortcuts: Confirm fast, reliable labeling with minimal clicks.

Deployment & Documentation

Provide a README or usage doc (how to run locally, environment variables for Phoenix API, etc.).

If needed, add a minimal CI/CD step to deploy or at least ensure tests pass.

Communicate final usage instructions to all reviewers.

Definition of Done

Users can load a batch of candidate documents pulled from Phoenix’s API and see them ranked by similarity_score.

Two reviewers can independently log in (by name or ID) and provide initial relevant/not relevant judgments with keyboard shortcuts.

After both finish, the system transitions items to final annotation phase, prioritizes entries with disagreement, and shows both reviewers’ initial labels side-by-side.

Users can set a final rating and provide text feedback collaboratively; changes auto-save and are pushed back into Phoenix’s golden dataset.

Final state = FINAL ANNOTATION COMPLETE with the correct rating.

Verified end-to-end on at least one test batch (the status changes and final data appear in Phoenix as expected).

