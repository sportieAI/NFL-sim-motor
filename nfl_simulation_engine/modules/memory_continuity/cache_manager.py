"""Cache manager for memory continuity in NFL simulation engine."""


class CacheManager:
    """Manages caching for memory continuity system."""
    
    def __init__(self, cache_dir=None, max_size=1000):
        self.cache_dir = cache_dir
        self.cache = {}
        self.max_size = max_size
    
    def get_cache(self, key):
        """Get value from cache."""
        return self.cache.get(key)
    
    def set_cache(self, key, value):
        """Set value in cache."""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove oldest
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value
    
    def has_cache(self, key):
        """Check if key exists in cache."""
        return key in self.cache
    
    def clear_cache(self):
        """Clear all cache."""
        self.cache.clear()
    
    def get(self, key):
        """Get value from cache (legacy method)."""
        return self.get_cache(key)
    
    def set(self, key, value):
        """Set value in cache (legacy method)."""
        self.set_cache(key, value)
    
    def clear(self):
        """Clear all cache (legacy method)."""
        self.clear_cache()
    
    def size(self):
        """Get cache size."""
        return len(self.cache)