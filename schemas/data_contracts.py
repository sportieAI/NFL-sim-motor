"""
JSONSchema definitions for NFL simulation engine data contracts.
"""

PLAY_EVENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "PlayEvent",
    "type": "object",
    "required": ["id", "timestamp", "type", "team_id", "down", "distance", "yard_line"],
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for the play event",
        },
        "timestamp": {"type": "number", "description": "Unix timestamp of the play"},
        "type": {
            "type": "string",
            "enum": ["run", "pass", "punt", "field_goal", "kickoff", "kneel", "spike"],
            "description": "Type of play executed",
        },
        "team_id": {
            "type": "string",
            "description": "ID of the team executing the play",
        },
        "down": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Current down (1-4)",
        },
        "distance": {
            "type": "integer",
            "minimum": 0,
            "description": "Yards to go for first down",
        },
        "yard_line": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "description": "Current yard line position",
        },
        "result": {
            "type": "object",
            "properties": {
                "yards_gained": {"type": "integer"},
                "touchdown": {"type": "boolean"},
                "first_down": {"type": "boolean"},
                "turnover": {"type": "boolean"},
                "penalty": {"type": "boolean"},
            },
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Semantic tags for the play",
        },
    },
}

DRIVE_SNAPSHOT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "DriveSnapshot",
    "type": "object",
    "required": ["drive_id", "team_id", "start_time", "plays"],
    "properties": {
        "drive_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for the drive",
        },
        "team_id": {"type": "string", "description": "ID of the team with possession"},
        "start_time": {
            "type": "number",
            "description": "Unix timestamp when drive started",
        },
        "end_time": {
            "type": ["number", "null"],
            "description": "Unix timestamp when drive ended",
        },
        "starting_field_position": {"type": "integer", "minimum": 1, "maximum": 100},
        "plays": {
            "type": "array",
            "items": {"$ref": "#/definitions/PlayEvent"},
            "description": "All plays in this drive",
        },
        "outcome": {
            "type": "string",
            "enum": [
                "touchdown",
                "field_goal",
                "punt",
                "turnover",
                "downs",
                "end_of_half",
            ],
            "description": "How the drive ended",
        },
        "score_delta": {
            "type": "integer",
            "description": "Points scored during this drive",
        },
    },
    "definitions": {"PlayEvent": PLAY_EVENT_SCHEMA},
}

NARRATIVE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Narrative",
    "type": "object",
    "required": ["id", "timestamp", "type", "content"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "timestamp": {"type": "number"},
        "type": {
            "type": "string",
            "enum": ["play_by_play", "drive_summary", "game_summary", "highlight"],
            "description": "Type of narrative content",
        },
        "content": {"type": "string", "description": "The narrative text"},
        "context": {
            "type": "object",
            "properties": {
                "play_id": {"type": ["string", "null"]},
                "drive_id": {"type": ["string", "null"]},
                "game_id": {"type": ["string", "null"]},
                "emotional_tone": {
                    "type": "string",
                    "enum": ["neutral", "exciting", "dramatic", "tense", "celebratory"],
                },
            },
        },
        "metadata": {
            "type": "object",
            "properties": {
                "generated_by": {"type": "string"},
                "model_version": {"type": "string"},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
    },
}

TAG_BUNDLE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TagBundle",
    "type": "object",
    "required": ["entity_id", "entity_type", "tags", "timestamp"],
    "properties": {
        "entity_id": {"type": "string", "description": "ID of the entity being tagged"},
        "entity_type": {
            "type": "string",
            "enum": ["play", "drive", "game", "player", "team"],
            "description": "Type of entity",
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["key", "value"],
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": ["string", "number", "boolean"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "source": {"type": "string"},
                    "version": {"type": "string"},
                },
            },
        },
        "timestamp": {"type": "number"},
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "SemVer version of tag ontology",
        },
    },
}

# Schema registry for validation
SCHEMAS = {
    "PlayEvent": PLAY_EVENT_SCHEMA,
    "DriveSnapshot": DRIVE_SNAPSHOT_SCHEMA,
    "Narrative": NARRATIVE_SCHEMA,
    "TagBundle": TAG_BUNDLE_SCHEMA,
}
