"""Unit tests for the pure helpers in :mod:`api.services.text_handler`.

This module holds the Python version of a single unit test that is also
expressed in TypeScript (``frontend/src/lib/question-id.test.ts``) and Rust
(``tests/rust/src/lib.rs``). All three exercise the same behaviour of the
parent-question-ID prefix logic.
"""

import unittest

from api.services.text_handler import _format_parent_question_id


class FormatParentQuestionIdTest(unittest.TestCase):
    """Tests for ``_format_parent_question_id``.

    The function prefixes an unprefixed parent question ID with the case-entry
    (``CE_``) or nature-code (``NC_``) prefix implied by its child question ID,
    and returns already-prefixed parent IDs unchanged.
    """

    def test_prefixes_unprefixed_parent_id_using_the_child_prefix(self):
        """An unprefixed parent ID receives the prefix implied by its child ID."""
        # Arrange
        question_id = "CE_1a"
        parent_question_id = "1"

        # Act
        result = _format_parent_question_id(question_id, parent_question_id)

        # Assert
        self.assertEqual(result, "CE_1")


if __name__ == "__main__":
    unittest.main()
