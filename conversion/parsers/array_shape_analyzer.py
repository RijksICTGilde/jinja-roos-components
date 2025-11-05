"""Analyze array shapes in defaultArgs to map to nested components."""

from typing import Dict, List, Any, Optional


class ArrayShapeAnalyzer:
    """Analyzer for mapping array items to component props."""

    def analyze_arrays(
        self,
        default_args: Dict[str, Any],
        nested_components: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze arrays in defaultArgs and map to nested components.

        Args:
            default_args: Default values dictionary (may contain arrays)
            nested_components: List of detected nested components with their props

        Returns:
            Dictionary mapping array attribute names to component mapping info:
            {
                'steps': {
                    'item_type': 'object',
                    'item_props': ['state', 'label', 'link', 'size', 'line'],
                    'maps_to_component': 'progress-tracker-step',
                    'component_tag': 'c-progress-tracker-step',
                    'match_score': 0.95  # How well the array items match the component
                }
            }
        """
        array_mappings = {}

        # Find all array attributes in default_args
        for attr_name, attr_value in default_args.items():
            if isinstance(attr_value, list) and len(attr_value) > 0:
                # Analyze the first item to get the shape
                first_item = attr_value[0]

                if isinstance(first_item, dict):
                    # Extract the keys (prop names) from the first item
                    item_props = list(first_item.keys())

                    # Try to match this shape with nested components
                    best_match = self._find_best_component_match(
                        item_props,
                        nested_components
                    )

                    if best_match:
                        array_mappings[attr_name] = {
                            'item_type': 'object',
                            'item_props': item_props,
                            'maps_to_component': best_match['name'],
                            'component_tag': best_match['tag_name'],
                            'component_class': best_match['component_class'],
                            'match_score': best_match['score']
                        }
                    else:
                        # No good match found
                        array_mappings[attr_name] = {
                            'item_type': 'object',
                            'item_props': item_props,
                            'maps_to_component': None,
                            'match_score': 0.0
                        }
                elif isinstance(first_item, str):
                    # Simple string array
                    array_mappings[attr_name] = {
                        'item_type': 'string',
                        'item_props': [],
                        'maps_to_component': None
                    }
                elif isinstance(first_item, (int, float)):
                    # Number array
                    array_mappings[attr_name] = {
                        'item_type': 'number',
                        'item_props': [],
                        'maps_to_component': None
                    }

        return array_mappings

    def _find_best_component_match(
        self,
        item_props: List[str],
        nested_components: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the best matching component for array item props.

        Args:
            item_props: List of prop names from array item
            nested_components: List of nested component metadata

        Returns:
            Best matching component with score, or None
        """
        best_match = None
        best_score = 0.0

        for component in nested_components:
            component_props = component.get('props', [])

            if not component_props:
                continue

            # Calculate match score: how many item props exist in component props
            matching_props = set(item_props) & set(component_props)
            if len(component_props) > 0:
                score = len(matching_props) / len(component_props)

                # Bonus if item has extra props that component can handle
                if len(matching_props) > 0:
                    item_coverage = len(matching_props) / len(item_props)
                    # Weighted average: prioritize component coverage
                    score = 0.7 * score + 0.3 * item_coverage

                if score > best_score and score > 0.5:  # Require at least 50% match
                    best_score = score
                    best_match = {
                        'name': component['name'],
                        'tag_name': component['tag_name'],
                        'component_class': component['component_class'],
                        'score': score
                    }

        return best_match

    def get_array_item_example(
        self,
        default_args: Dict[str, Any],
        attr_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get an example array item for an attribute.

        Args:
            default_args: Default values dictionary
            attr_name: Array attribute name

        Returns:
            First item from the array, or None
        """
        if attr_name in default_args:
            value = default_args[attr_name]
            if isinstance(value, list) and len(value) > 0:
                return value[0]

        return None
