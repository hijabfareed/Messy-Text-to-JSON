
# Domain: Job Posts
# Purpose: Test retry behavior without calling the Gemini API.

import unittest
from unittest.mock import patch

from extract import extract_job
from schema import Extracted


class TestRetryMechanism(unittest.TestCase):

    def test_retry_after_validation_error(self):

        # Simulate an invalid first response.
        invalid_response = '{"job_title": 123}'

        # Simulate a corrected second response.
        valid_response = Extracted(
            job_title="Python Developer",
            company="CloudCore Technologies",
            location="Lahore"
        ).model_dump_json()

        # Replace the real API function during testing.
        with patch("extract.API_KEY", "test-key"), \
             patch("extract.genai.Client"), \
             patch(
                 "extract.ask",
                 side_effect=[
                     invalid_response,
                     valid_response
                 ]
             ) as mock_ask:

            result = extract_job(
                "Python Developer needed in Lahore."
            )

            # Verify successful extraction.
            self.assertIsNotNone(result)

            self.assertEqual(
                result.job_title,
                "Python Developer"
            )

            # Verify exactly two attempts occurred.
            self.assertEqual(mock_ask.call_count, 2)

            # Verify feedback was sent on the second attempt.
            feedback = mock_ask.call_args_list[1].args[3]

            self.assertIn(
                "Validation error",
                feedback
            )

    def test_failure_after_three_attempts(self):

        # Simulate three invalid responses.
        invalid_response = '{"job_title": 123}'

        with patch("extract.API_KEY", "test-key"), \
             patch("extract.genai.Client"), \
             patch(
                 "extract.ask",
                 return_value=invalid_response
             ) as mock_ask:

            result = extract_job("Invalid test input")

            # Verify extraction failed.
            self.assertIsNone(result)

            # Verify exactly three attempts occurred.
            self.assertEqual(mock_ask.call_count, 3)


if __name__ == "__main__":
    unittest.main()
