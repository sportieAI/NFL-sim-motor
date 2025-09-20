class Narrator:
    """Simple template-based play-by-play narrator."""

    def narrate(self, play, cluster):
        desc = play.get("description", "Unknown play")
        team = play.get("team", "Team")
        tags = play.get("tags", [])
        cluster_str = cluster
        return f"{team}: {desc} [{', '.join(tags) if tags else 'no tags'}] (Cluster: {cluster_str})"
