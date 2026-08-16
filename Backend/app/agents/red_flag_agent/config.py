# Red Flag Agent Configuration

# Database Collections
COLLECTION_EXTRACTED_METRICS = "extracted_metrics"
COLLECTION_DERIVED_METRICS = "derived_metrics"
COLLECTION_RED_FLAGS = "red_flags"
COLLECTION_CHUNKS = "parsed_chunks"
COLLECTION_EMBEDDINGS = "embeddings"

# LLM Configuration
LLM_MODEL = "gpt-4o"

# Quantitative Thresholds (MVP Defaults)
THRESHOLDS = {
    "debt_growth_percentage": 20.0,           # > 20% YoY increase
    "sudden_change_percentage": 50.0,         # > 50% YoY movement
    "debt_to_equity_ratio": 2.0,              # > 2.0 D/E
    "margin_compression_points": 5.0,         # > 5.0 percentage points drop
    "profit_decline_percentage": 20.0,        # > 20% YoY decrease
}

# Supported Qualitative Categories for V1
QUALITATIVE_CATEGORIES = [
    "Going Concern",
    "Auditor Qualifications",
    "Material Weaknesses"
]
