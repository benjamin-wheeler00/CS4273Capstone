//! Rust version of a single unit test that is also expressed in Python
//! (`backend/tests/test_text_handler.py`) and TypeScript
//! (`frontend/src/lib/question-id.test.ts`).

/// Prefixes an unprefixed parent question ID with the case-entry (`CE_`) or
/// nature-code (`NC_`) prefix implied by its child question ID.
///
/// Already-prefixed parent IDs are returned unchanged. This mirrors the
/// backend's `_format_parent_question_id` in `api/services/text_handler.py`.
pub fn format_parent_question_id(question_id: &str, parent_question_id: &str) -> String {
    if parent_question_id.starts_with("CE_") || parent_question_id.starts_with("NC_") {
        return parent_question_id.to_string();
    }

    let prefix = if question_id.starts_with("CE_") { "CE" } else { "NC" };
    format!("{prefix}_{parent_question_id}")
}

#[cfg(test)]
mod tests {
    use super::format_parent_question_id;

    #[test]
    fn prefixes_unprefixed_parent_id_using_the_child_prefix() {
        // Arrange
        let question_id = "CE_1a";
        let parent_question_id = "1";

        // Act
        let result = format_parent_question_id(question_id, parent_question_id);

        // Assert
        assert_eq!(result, "CE_1");
    }
}
