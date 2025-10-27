"""
Enhanced API key management for microservices with intelligent load balancing.
"""

import os
import time
import random
import asyncio
import logging
from typing import List, Optional, Dict, Tuple
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class APIKeyStats:
    """Statistics for an API key"""
    key_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_used: Optional[datetime] = None
    current_load: int = 0  # Current concurrent requests
    rate_limit_hits: int = 0
    average_response_time: float = 0.0
    is_healthy: bool = True

class APIKeyManager:
    """
    Advanced API key manager with intelligent load balancing and health monitoring.
    Optimized for high-concurrency microservices architecture.
    """
    
    def __init__(self, keys_file_path: str = None):
        self.keys_file_path = keys_file_path or self._find_keys_file()
        self.api_keys: List[str] = []
        self.key_stats: Dict[str, APIKeyStats] = {}
        self.request_times: Dict[str, List[float]] = defaultdict(list)
        self.rate_limit_windows: Dict[str, List[float]] = defaultdict(list)
        
        # Configuration
        self.max_requests_per_minute = int(os.getenv("API_MAX_REQUESTS_PER_MINUTE", "1800"))
        self.rate_limit_window = 60  # seconds
        self.health_check_interval = int(os.getenv("API_HEALTH_CHECK_INTERVAL", "300"))  # 5 minutes
        self.max_concurrent_per_key = int(os.getenv("API_MAX_CONCURRENT_PER_KEY", "50"))
        
        # Thread safety
        self.lock = Lock()
        
        # Load keys and initialize
        self._load_keys()
        self._initialize_stats()
        
        logger.info(f"APIKeyManager initialized with {len(self.api_keys)} keys")
    
    def _find_keys_file(self) -> str:
        """Find the API keys file in the project structure"""
        possible_paths = [
            "api_rotation/API_Keys.txt",
            "../api_rotation/API_Keys.txt",
            "../../api_rotation/API_Keys.txt",
            "../../../api_rotation/API_Keys.txt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default fallback
        return "API_Keys.txt"
    
    def _load_keys(self) -> None:
        """Load API keys from file"""
        try:
            if not os.path.exists(self.keys_file_path):
                logger.error(f"API keys file not found: {self.keys_file_path}")
                return
            
            with open(self.keys_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            self.api_keys = [line.strip() for line in lines if line.strip()]
            logger.info(f"Loaded {len(self.api_keys)} API keys")
            
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            self.api_keys = []
    
    def _initialize_stats(self) -> None:
        """Initialize statistics for all API keys"""
        for i, key in enumerate(self.api_keys):
            key_id = f"key_{i+1}"
            self.key_stats[key_id] = APIKeyStats(key_id=key_id)
    
    def _clean_old_requests(self, key_id: str) -> None:
        """Clean old request timestamps outside the rate limit window"""
        current_time = time.time()
        cutoff_time = current_time - self.rate_limit_window
        
        # Clean rate limit tracking
        self.rate_limit_windows[key_id] = [
            req_time for req_time in self.rate_limit_windows[key_id]
            if req_time > cutoff_time
        ]
        
        # Clean response time tracking (keep last 100 requests)
        if len(self.request_times[key_id]) > 100:
            self.request_times[key_id] = self.request_times[key_id][-100:]
    
    def _calculate_key_score(self, key_id: str) -> float:
        """
        Calculate a score for key selection based on multiple factors.
        Lower score = better choice.
        """
        stats = self.key_stats[key_id]
        
        if not stats.is_healthy:
            return float('inf')  # Never select unhealthy keys
        
        # Base score factors
        load_factor = stats.current_load / self.max_concurrent_per_key
        rate_limit_factor = len(self.rate_limit_windows[key_id]) / self.max_requests_per_minute
        
        # Response time factor (normalized)
        response_time_factor = 0
        if self.request_times[key_id]:
            avg_response_time = sum(self.request_times[key_id]) / len(self.request_times[key_id])
            response_time_factor = min(avg_response_time / 10.0, 1.0)  # Cap at 10 seconds
        
        # Recent failures factor
        failure_rate = 0
        if stats.total_requests > 0:
            failure_rate = stats.failed_requests / stats.total_requests
        
        # Combine factors with weights
        score = (
            load_factor * 0.4 +           # 40% weight on current load
            rate_limit_factor * 0.3 +     # 30% weight on rate limiting
            response_time_factor * 0.2 +  # 20% weight on response time
            failure_rate * 0.1            # 10% weight on failure rate
        )
        
        return score
    
    def get_best_key(self) -> Optional[Tuple[str, str]]:
        """
        Get the best available API key based on current load and performance.
        Returns tuple of (key_id, api_key) or None if no keys available.
        """
        with self.lock:
            if not self.api_keys:
                logger.error("No API keys available")
                return None
            
            # Clean old request data for all keys
            for key_id in self.key_stats.keys():
                self._clean_old_requests(key_id)
            
            # Find the best key based on scoring
            best_key_id = None
            best_score = float('inf')
            
            for i, key in enumerate(self.api_keys):
                key_id = f"key_{i+1}"
                
                # Check if key is within rate limits
                if len(self.rate_limit_windows[key_id]) >= self.max_requests_per_minute:
                    continue
                
                # Check if key is not overloaded
                if self.key_stats[key_id].current_load >= self.max_concurrent_per_key:
                    continue
                
                score = self._calculate_key_score(key_id)
                if score < best_score:
                    best_score = score
                    best_key_id = key_id
            
            if best_key_id is None:
                logger.warning("All API keys are rate limited or overloaded")
                # Fallback: use random key with lowest load
                available_keys = [
                    (f"key_{i+1}", key) for i, key in enumerate(self.api_keys)
                    if self.key_stats[f"key_{i+1}"].is_healthy
                ]
                if available_keys:
                    best_key_id, selected_key = min(
                        available_keys,
                        key=lambda x: self.key_stats[x[0]].current_load
                    )
                    return best_key_id, selected_key
                return None
            
            # Record the request
            current_time = time.time()
            self.rate_limit_windows[best_key_id].append(current_time)
            self.key_stats[best_key_id].current_load += 1
            self.key_stats[best_key_id].total_requests += 1
            self.key_stats[best_key_id].last_used = datetime.now()
            
            selected_key = self.api_keys[int(best_key_id.split('_')[1]) - 1]
            
            logger.debug(f"Selected {best_key_id} with score {best_score:.3f}")
            return best_key_id, selected_key
    
    def record_request_completion(self, key_id: str, success: bool, response_time: float) -> None:
        """Record the completion of a request"""
        with self.lock:
            if key_id not in self.key_stats:
                return
            
            stats = self.key_stats[key_id]
            stats.current_load = max(0, stats.current_load - 1)
            
            if success:
                stats.successful_requests += 1
                self.request_times[key_id].append(response_time)
                
                # Update average response time
                if self.request_times[key_id]:
                    stats.average_response_time = sum(self.request_times[key_id]) / len(self.request_times[key_id])
            else:
                stats.failed_requests += 1
                
                # Mark as unhealthy if too many recent failures
                if stats.total_requests > 10:
                    recent_failure_rate = stats.failed_requests / stats.total_requests
                    if recent_failure_rate > 0.5:  # More than 50% failure rate
                        stats.is_healthy = False
                        logger.warning(f"Marked {key_id} as unhealthy due to high failure rate")
    
    def record_rate_limit_hit(self, key_id: str) -> None:
        """Record a rate limit hit for a key"""
        with self.lock:
            if key_id in self.key_stats:
                self.key_stats[key_id].rate_limit_hits += 1
                logger.warning(f"Rate limit hit for {key_id}")
    
    def mark_key_healthy(self, key_id: str) -> None:
        """Mark a key as healthy (useful for recovery)"""
        with self.lock:
            if key_id in self.key_stats:
                self.key_stats[key_id].is_healthy = True
                logger.info(f"Marked {key_id} as healthy")
    
    def get_stats(self) -> Dict[str, Dict]:
        """Get statistics for all API keys"""
        with self.lock:
            stats = {}
            for key_id, key_stats in self.key_stats.items():
                stats[key_id] = {
                    'total_requests': key_stats.total_requests,
                    'successful_requests': key_stats.successful_requests,
                    'failed_requests': key_stats.failed_requests,
                    'current_load': key_stats.current_load,
                    'rate_limit_hits': key_stats.rate_limit_hits,
                    'average_response_time': key_stats.average_response_time,
                    'is_healthy': key_stats.is_healthy,
                    'last_used': key_stats.last_used.isoformat() if key_stats.last_used else None,
                    'current_rate_limit_usage': len(self.rate_limit_windows[key_id]),
                    'score': self._calculate_key_score(key_id) if key_stats.is_healthy else float('inf')
                }
            return stats
    
    def get_total_capacity(self) -> Dict[str, int]:
        """Get total system capacity information"""
        healthy_keys = sum(1 for stats in self.key_stats.values() if stats.is_healthy)
        return {
            'total_keys': len(self.api_keys),
            'healthy_keys': healthy_keys,
            'max_requests_per_minute': healthy_keys * self.max_requests_per_minute,
            'max_concurrent_requests': healthy_keys * self.max_concurrent_per_key,
            'current_load': sum(stats.current_load for stats in self.key_stats.values())
        }
    
    def reload_keys(self) -> bool:
        """Reload API keys from file"""
        with self.lock:
            old_count = len(self.api_keys)
            self._load_keys()
            self._initialize_stats()
            new_count = len(self.api_keys)
            
            logger.info(f"Reloaded API keys: {old_count} -> {new_count}")
            return new_count > 0

# Global API key manager instance
api_key_manager = APIKeyManager()

# Convenience functions for services
async def get_api_key() -> Optional[Tuple[str, str]]:
    """Get the best available API key"""
    return api_key_manager.get_best_key()

async def record_api_request(key_id: str, success: bool, response_time: float) -> None:
    """Record API request completion"""
    api_key_manager.record_request_completion(key_id, success, response_time)

async def record_rate_limit(key_id: str) -> None:
    """Record rate limit hit"""
    api_key_manager.record_rate_limit_hit(key_id)

async def get_api_stats() -> Dict[str, Dict]:
    """Get API key statistics"""
    return api_key_manager.get_stats()
