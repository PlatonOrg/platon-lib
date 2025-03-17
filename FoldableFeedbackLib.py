"""
FoldableFeedbackLib.py

A utility module for managing foldable feedback content with categories and feedback items.

Changelog:
----------
v1.2.0 - 2024-12-06
- Added a helper function `_truncate_field` to centralize and reuse truncation logic.
- Applied `_truncate_field` to `expected` and `obtained` fields in `add_feedback` and `add_to_last_feedback`.
- Updated the docstrings for `add_feedback` and `add_to_last_feedback` to reflect truncation behavior.
- Added a configurable `max_length` parameter for truncation, defaulting to 1000 characters.

v1.1.0 - 2024-11-07
- Added type hints for all parameters and return types to improve readability and enable static code analysis.
- Refactored feedback update logic into a helper method `_update_feedback` to reduce code duplication.
- Replaced generic `Exception` with `TypeError` for more specific error handling in `add_category` and `add_to_last_category`.
- Added docstrings for each method to document purpose and usage.
- Improved `get_last_category` by using an early return pattern for better readability.

v1.0.0 - Initial Release
- Implemented core functionalities for adding feedback and categories.
- Included `add_feedback`, `add_to_last_feedback`, `add_category`, `add_to_last_category`, and `get_last_category` methods.
"""

from typing import List, Union, Optional, Dict, Any

class FoldableFeedbackContent:
    def __init__(self):
        self.content: List[Dict[str, Any]] = []

    @staticmethod
    def _truncate_field(value: str, max_length: int = 1000) -> str:
        """Truncates the field value if it exceeds the max_length.
        
        Keeps the first and last 250 characters and inserts a note in between.
        """
        if len(value) > max_length:
            return value[:250] + " ... (result too long) ... " + value[-250:]
        return value

    def add_feedback(
        self,
        name: str,
        description: str = "",
        expected: str = "",
        obtained: str = "",
        arguments: str = "",
        display: bool = False,
        feedback_type: str = "info",
        max_length: int = 1000
    ) -> None:
        """Adds a feedback item to the content list.

        The `expected` and `obtained` fields are truncated if they exceed the `max_length`.
        """
        expected = self._truncate_field(expected, max_length)
        obtained = self._truncate_field(obtained, max_length)

        self.content.append({
            "name": name,
            "description": description,
            "expected": expected,
            "obtained": obtained,
            "arguments": arguments,
            "display": display,
            "type": feedback_type
        })

    def add_to_last_feedback(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        expected: Optional[str] = None,
        obtained: Optional[str] = None,
        arguments: Optional[str] = None,
        display: Optional[bool] = None,
        feedback_type: Optional[str] = None,
        max_length: int = 1000
    ) -> None:
        """Updates the last feedback item with provided attributes.

        The `expected` and `obtained` fields are truncated if they exceed the `max_length`.
        """
        if self.content:
            for feedback in reversed(self.content):
                if "feedbacks" not in feedback:
                    if expected is not None:
                        expected = self._truncate_field(expected, max_length)
                    if obtained is not None:
                        obtained = self._truncate_field(obtained, max_length)

                    self._update_feedback(feedback, name, description, expected, obtained, arguments, display, feedback_type)
                    break

    def add_category(
        self,
        name: str,
        description: str = "",
        display: bool = False,
        feedback_type: str = "info",
        feedbacks: Optional[Union[List[Dict[str, Any]], 'FoldableFeedbackContent']] = None
    ) -> None:
        """Adds a feedback category to the content list."""
        if feedbacks is None:
            feedbacks = []
        elif isinstance(feedbacks, FoldableFeedbackContent):
            feedbacks = feedbacks.get()
        
        if isinstance(feedbacks, list):
            self.content.append({
                "name": name,
                "description": description,
                "display": display,
                "type": feedback_type,
                "feedbacks": feedbacks
            })
        else:
            raise TypeError("Feedbacks must be a list or a FoldableFeedbackContent object")
        
    def add_to_last_category(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        display: Optional[bool] = None,
        feedback_type: Optional[str] = None,
        feedbacks: Optional[Union[List[Dict[str, Any]], 'FoldableFeedbackContent']] = None
    ) -> None:
        """Updates the last category with provided attributes."""
        if self.content:
            for feedback in reversed(self.content):
                if "feedbacks" in feedback:
                    self._update_feedback(feedback, name, description, display=display, feedback_type=feedback_type)
                    if feedbacks is not None:
                        if isinstance(feedbacks, list):
                            feedback["feedbacks"].extend(feedbacks)
                        elif isinstance(feedbacks, FoldableFeedbackContent):
                            feedback["feedbacks"].extend(feedbacks.get())
                        else:
                            raise TypeError("Feedbacks must be a list or a FoldableFeedbackContent object")
                    break
        
    def get_last_category(self) -> Optional[Dict[str, Any]]:
        """Returns the last category or None if no categories exist."""
        return next((f for f in reversed(self.content) if "feedbacks" in f), None)

    def get(self) -> List[Dict[str, Any]]:
        """Returns all feedback content."""
        return self.content

    def _update_feedback(
        self,
        feedback: Dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        expected: Optional[str] = None,
        obtained: Optional[str] = None,
        arguments: Optional[str] = None,
        display: Optional[bool] = None,
        feedback_type: Optional[str] = None
    ) -> None:
        """Helper to update feedback fields with non-None values."""
        if name is not None:
            feedback["name"] = name
        if description is not None:
            feedback["description"] = description
        if expected is not None:
            feedback["expected"] = expected
        if obtained is not None:
            feedback["obtained"] = obtained
        if arguments is not None:
            feedback["arguments"] = arguments
        if display is not None:
            feedback["display"] = display
        if feedback_type is not None:
            feedback["type"] = feedback_type
