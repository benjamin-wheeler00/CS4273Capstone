import { describe, it } from "node:test";
import assert from "node:assert/strict";

import { formatParentQuestionId } from "./question-id.ts";

// TypeScript version of the same single unit test also written in Python
// (backend/tests/test_text_handler.py) and Rust (tests/rust/src/lib.rs).
describe("formatParentQuestionId", () => {
  it("prefixes an unprefixed parent ID using the prefix implied by the child ID", () => {
    // Arrange
    const questionId = "CE_1a";
    const parentQuestionId = "1";

    // Act
    const result = formatParentQuestionId(questionId, parentQuestionId);

    // Assert
    assert.equal(result, "CE_1");
  });
});
