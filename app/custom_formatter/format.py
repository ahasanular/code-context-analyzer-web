from code_context_analyzer.formatters.default import LegacyCodeFormatter
from typing import List, Dict, Any


class CustomFormatter(LegacyCodeFormatter):
    def format(self, parsed_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate the complete markup report"""
        self.parsed_data = parsed_data

        self.project_name = self._extract_project_name()

        heading = self._generate_heading()
        tree = self._generate_tree()
        description = self._generate_detailed_description()

        # Optionally concatenate all for truncation check
        full_report = f"{heading}\n\n## Tree Structure:\n{tree}\n\n## Detailed Description:\n{description}"

        # Apply truncation if needed
        if self.truncate_total and len(full_report) > self.truncate_total:
            allowed_length = self.truncate_total
            truncated_report = full_report[
                                   :allowed_length] + "\n\n... (truncated due to length)"

            # You could split back truncated parts (less precise), or just return the truncated string in one field.
            return {
                "heading": heading,
                "tree": tree,
                "details": description,
                "full": truncated_report
            }

        return {
            "heading": heading,
            "tree": tree,
            "details": description
        }