from typing import Optional, Tuple

class ValueNormalizer:
    @staticmethod
    def normalize(value: Optional[float], original_value: Optional[str], unit: Optional[str]) -> Tuple[Optional[float], str]:
        """
        Normalizes the numeric value based on the scale and original string.
        Returns a tuple of (normalized_value, final_unit).
        
        Example:
            value=125.4, unit="billion" -> 125400000000.0, "absolute"
            value=5.2, original_value="(5.2 million)", unit="million" -> -5200000.0, "absolute"
        """
        if value is None:
            return None, unit or "absolute"
            
        final_value = float(value)
        
        # Determine if it should be negative based on common financial parentheses notation
        if original_value and ("(" in original_value and ")" in original_value):
            final_value = -abs(final_value)
            
        final_unit = "absolute"
        
        # Apply scaling based on unit
        if unit:
            unit_lower = unit.lower().strip()
            if "billion" in unit_lower:
                final_value *= 1_000_000_000
            elif "million" in unit_lower:
                final_value *= 1_000_000
            elif "thousand" in unit_lower:
                final_value *= 1_000
            elif "percent" in unit_lower or "%" in unit_lower:
                # Keep percentage as is, but mark the unit
                final_unit = "percent"
            else:
                final_unit = unit_lower
                
        return final_value, final_unit
