/**
 * Prefixes an unprefixed parent question ID with the case-entry (`CE_`) or
 * nature-code (`NC_`) prefix implied by its child question ID.
 *
 * Already-prefixed parent IDs are returned unchanged. This mirrors the
 * backend's `_format_parent_question_id` in `api/services/text_handler.py`.
 */
export function formatParentQuestionId(
  questionId: string,
  parentQuestionId: string,
): string {
  if (parentQuestionId.startsWith("CE_") || parentQuestionId.startsWith("NC_")) {
    return parentQuestionId;
  }

  const prefix = questionId.startsWith("CE_") ? "CE" : "NC";
  return `${prefix}_${parentQuestionId}`;
}
