"""
Versioned ontology management system with semantic versioning.
Supports backward compatibility and deprecation windows.
"""

import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
import hashlib


class VersionStatus(Enum):
    """Status of ontology versions."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    OBSOLETE = "obsolete"
    DRAFT = "draft"


@dataclass
class SemanticVersion:
    """Semantic version following semver.org standards."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def is_compatible(self, other: "SemanticVersion") -> bool:
        """Check if this version is backward compatible with another."""
        return self.major == other.major and self >= other

    @classmethod
    def from_string(cls, version_str: str) -> "SemanticVersion":
        """Parse version from string."""
        parts = version_str.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))


@dataclass
class TagDefinition:
    """Definition of a tag in the ontology."""

    tag_name: str
    description: str
    category: str
    expected_confidence_range: Tuple[float, float]  # (min, max)
    deprecated: bool = False
    deprecation_date: Optional[float] = None
    replacement_tag: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None


@dataclass
class TagInstance:
    """Instance of a tag with confidence and metadata."""

    tag_name: str
    confidence: float
    timestamp: float
    context: Dict[str, Any]
    version: str


@dataclass
class OntologyVersion:
    """Complete version of the ontology."""

    version: SemanticVersion
    status: VersionStatus
    tag_definitions: Dict[str, TagDefinition]
    release_date: float
    deprecation_date: Optional[float]
    changelog: str
    hash_signature: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": str(self.version),
            "status": self.status.value,
            "tag_definitions": {k: asdict(v) for k, v in self.tag_definitions.items()},
            "release_date": self.release_date,
            "deprecation_date": self.deprecation_date,
            "changelog": self.changelog,
            "hash_signature": self.hash_signature,
        }


class OntologyManager:
    """Manages versioned ontologies with deprecation and backward compatibility."""

    def __init__(self, storage_path: str = "ontology/schemas"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.versions: Dict[str, OntologyVersion] = {}
        self.current_version: Optional[SemanticVersion] = None
        self.logger = logging.getLogger(__name__)

        # Load existing versions
        self._load_versions()

        # Initialize with base ontology if none exists
        if not self.versions:
            self._initialize_base_ontology()

    def _load_versions(self):
        """Load all ontology versions from storage."""
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                version = SemanticVersion.from_string(data["version"])
                version_obj = OntologyVersion(
                    version=version,
                    status=VersionStatus(data["status"]),
                    tag_definitions={
                        k: TagDefinition(**v)
                        for k, v in data["tag_definitions"].items()
                    },
                    release_date=data["release_date"],
                    deprecation_date=data.get("deprecation_date"),
                    changelog=data["changelog"],
                    hash_signature=data["hash_signature"],
                )

                self.versions[str(version)] = version_obj

                if version_obj.status == VersionStatus.ACTIVE:
                    if not self.current_version or version > self.current_version:
                        self.current_version = version

            except Exception as e:
                self.logger.error(
                    f"Failed to load ontology version from {file_path}: {e}"
                )

    def _initialize_base_ontology(self):
        """Initialize base ontology with fundamental NFL tags."""
        base_tags = {
            "aggressive": TagDefinition(
                tag_name="aggressive",
                description="Play calling that prioritizes high-risk, high-reward strategies",
                category="strategy",
                expected_confidence_range=(0.0, 1.0),
            ),
            "conservative": TagDefinition(
                tag_name="conservative",
                description="Play calling that prioritizes ball control and low risk",
                category="strategy",
                expected_confidence_range=(0.0, 1.0),
            ),
            "redzone": TagDefinition(
                tag_name="redzone",
                description="Play occurring in the red zone (within 20 yards of goal)",
                category="field_position",
                expected_confidence_range=(0.8, 1.0),
            ),
            "two_minute_drill": TagDefinition(
                tag_name="two_minute_drill",
                description="Play occurring during two-minute warning situation",
                category="timing",
                expected_confidence_range=(0.9, 1.0),
            ),
            "third_down_conversion": TagDefinition(
                tag_name="third_down_conversion",
                description="Critical third down conversion attempt",
                category="down_distance",
                expected_confidence_range=(0.7, 1.0),
            ),
        }

        version = SemanticVersion(1, 0, 0)
        self.create_version(
            version=version,
            tag_definitions=base_tags,
            changelog="Initial ontology with fundamental NFL play tags",
        )

    def create_version(
        self,
        version: SemanticVersion,
        tag_definitions: Dict[str, TagDefinition],
        changelog: str,
        status: VersionStatus = VersionStatus.ACTIVE,
    ) -> bool:
        """Create a new ontology version."""
        # Generate hash signature
        content = json.dumps(
            {k: asdict(v) for k, v in tag_definitions.items()}, sort_keys=True
        )
        hash_signature = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Create version object
        version_obj = OntologyVersion(
            version=version,
            status=status,
            tag_definitions=tag_definitions,
            release_date=time.time(),
            deprecation_date=None,
            changelog=changelog,
            hash_signature=hash_signature,
        )

        # Deprecate previous active version if this is newer
        if status == VersionStatus.ACTIVE:
            for existing_version in self.versions.values():
                if (
                    existing_version.status == VersionStatus.ACTIVE
                    and existing_version.version < version
                ):
                    existing_version.status = VersionStatus.DEPRECATED
                    existing_version.deprecation_date = time.time()

            self.current_version = version

        # Store version
        self.versions[str(version)] = version_obj

        # Persist to disk
        return self._save_version(version_obj)

    def _save_version(self, version: OntologyVersion) -> bool:
        """Save version to disk."""
        try:
            file_path = self.storage_path / f"ontology_v{version.version}.json"
            with open(file_path, "w") as f:
                json.dump(version.to_dict(), f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save ontology version {version.version}: {e}")
            return False

    def get_current_tags(self) -> Dict[str, TagDefinition]:
        """Get tag definitions from current active version."""
        if not self.current_version:
            return {}

        current = self.versions.get(str(self.current_version))
        return current.tag_definitions if current else {}

    def get_version_tags(self, version: str) -> Dict[str, TagDefinition]:
        """Get tag definitions from specific version."""
        version_obj = self.versions.get(version)
        return version_obj.tag_definitions if version_obj else {}

    def add_tag(self, tag_def: TagDefinition, minor_version_bump: bool = True) -> bool:
        """Add a new tag to the current ontology."""
        if not self.current_version:
            return False

        current = self.versions[str(self.current_version)]
        new_tags = current.tag_definitions.copy()
        new_tags[tag_def.tag_name] = tag_def

        # Create new version
        if minor_version_bump:
            new_version = SemanticVersion(
                self.current_version.major, self.current_version.minor + 1, 0
            )
        else:
            new_version = SemanticVersion(
                self.current_version.major,
                self.current_version.minor,
                self.current_version.patch + 1,
            )

        return self.create_version(
            version=new_version,
            tag_definitions=new_tags,
            changelog=f"Added tag: {tag_def.tag_name} - {tag_def.description}",
        )

    def deprecate_tag(
        self, tag_name: str, replacement_tag: Optional[str] = None
    ) -> bool:
        """Deprecate a tag in the current ontology."""
        if not self.current_version:
            return False

        current = self.versions[str(self.current_version)]
        if tag_name not in current.tag_definitions:
            return False

        new_tags = current.tag_definitions.copy()
        new_tags[tag_name].deprecated = True
        new_tags[tag_name].deprecation_date = time.time()
        new_tags[tag_name].replacement_tag = replacement_tag

        # Minor version bump for deprecation
        new_version = SemanticVersion(
            self.current_version.major, self.current_version.minor + 1, 0
        )

        changelog = f"Deprecated tag: {tag_name}"
        if replacement_tag:
            changelog += f" (replaced by {replacement_tag})"

        return self.create_version(
            version=new_version, tag_definitions=new_tags, changelog=changelog
        )

    def validate_tag_confidence(self, tag_name: str, confidence: float) -> bool:
        """Validate that tag confidence is within expected range."""
        tags = self.get_current_tags()
        if tag_name not in tags:
            return False

        tag_def = tags[tag_name]
        min_conf, max_conf = tag_def.expected_confidence_range
        return min_conf <= confidence <= max_conf

    def get_migration_path(
        self, from_version: str, to_version: str
    ) -> List[Dict[str, Any]]:
        """Get migration instructions between two versions."""
        from_ver = self.versions.get(from_version)
        to_ver = self.versions.get(to_version)

        if not from_ver or not to_ver:
            return []

        migrations = []

        # Find deprecated/removed tags
        from_tags = set(from_ver.tag_definitions.keys())
        to_tags = set(to_ver.tag_definitions.keys())

        removed_tags = from_tags - to_tags
        added_tags = to_tags - from_tags

        for tag in removed_tags:
            original_tag = from_ver.tag_definitions[tag]
            migration = {
                "action": "remove_tag",
                "tag": tag,
                "replacement": original_tag.replacement_tag,
            }
            migrations.append(migration)

        for tag in added_tags:
            migration = {
                "action": "add_tag",
                "tag": tag,
                "definition": asdict(to_ver.tag_definitions[tag]),
            }
            migrations.append(migration)

        return migrations

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get complete version history."""
        history = []
        for version_str, version_obj in sorted(
            self.versions.items(), key=lambda x: x[1].version
        ):
            history.append(
                {
                    "version": version_str,
                    "status": version_obj.status.value,
                    "release_date": version_obj.release_date,
                    "deprecation_date": version_obj.deprecation_date,
                    "changelog": version_obj.changelog,
                    "tag_count": len(version_obj.tag_definitions),
                }
            )
        return history
