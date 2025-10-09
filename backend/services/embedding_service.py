import os
# Suppress ALTS and gRPC warnings early
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''

import google.generativeai as genai
from typing import List
import sys
import asyncio
import concurrent.futures
from utils.logger import chat_logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from api_rotation.api_key_rotator import api_key_rotator
    ROTATION_ENABLED = True
    chat_logger.info("API key rotation enabled for embeddings")
except ImportError as e:
    chat_logger.warning("API key rotation not available for embeddings", error=str(e))
    ROTATION_ENABLED = False

embedding_pool = concurrent.futures.ThreadPoolExecutor(max_workers=50)

class EmbeddingService:
    """Service for generating embeddings using Gemini with API rotation"""
    
    @staticmethod
    def get_rotated_api_key() -> str:
        """Get next API key from rotation"""
        if ROTATION_ENABLED:
            api_key = api_key_rotator.get_next_key()
            if api_key:
                return api_key
            chat_logger.warning("API rotation failed, falling back to settings")
        
        from config.settings import settings
        return settings.GEMINI_API_KEY
    
    @staticmethod
    def get_all_api_keys():
        """Get all available API keys for fallback attempts"""
        keys = []
        
        # Try to get keys from rotation
        if ROTATION_ENABLED:
            try:
                # Get all keys from the rotator
                all_keys = api_key_rotator.api_keys if hasattr(api_key_rotator, 'api_keys') else []
                keys.extend(all_keys)
            except Exception as e:
                chat_logger.warning("Failed to get keys from rotation", error=str(e))
        
        # Add settings key as fallback
        from config.settings import settings
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in keys:
            keys.append(settings.GEMINI_API_KEY)
        
        return keys
    
    @staticmethod
    async def generate_embedding(text: str, max_retries: int = 1) -> List[float]:
        """
        Generate embedding for a single text with multi-key fallback
        
        REDUCED RETRIES: Only 1 retry per key to prevent quota exhaustion
        14 keys × 1 retry = 14 attempts max (was 28)
        """
        loop = asyncio.get_event_loop()
        
        # Get all available API keys for fallback
        all_keys = EmbeddingService.get_all_api_keys()
        
        # Circuit breaker: stop early if too many consecutive quota failures
        consecutive_quota_failures = 0
        max_consecutive_failures = 5
        
        # Try each key
        for key_index, api_key in enumerate(all_keys):
            # Stop early if 5+ keys in a row failed with quota
            if consecutive_quota_failures >= max_consecutive_failures:
                chat_logger.warning(f"Circuit breaker: {consecutive_quota_failures} consecutive quota failures, stopping early")
                from google.api_core.exceptions import ResourceExhausted
                raise ResourceExhausted(f"Circuit breaker: {consecutive_quota_failures} consecutive API keys exhausted")
            
            for attempt in range(max_retries):
                def _generate():
                    try:
                        genai.configure(api_key=api_key)
                        
                        # Truncate text if too long (max 2048 tokens ~= 8000 chars)
                        text_truncated = text[:8000] if len(text) > 8000 else text
                        
                        result = genai.embed_content(
                            model="models/embedding-001",
                            content=text_truncated,
                            task_type="retrieval_document"
                        )
                        return result['embedding'], None
                    except Exception as e:
                        return None, e
                
                try:
                    embedding, error = await loop.run_in_executor(embedding_pool, _generate)
                    
                    if embedding:
                        # Success! Reset consecutive failures counter
                        consecutive_quota_failures = 0
                        return embedding
                    
                    if error:
                        error_str = str(error).lower()
                        
                        # Check if it's a quota error
                        if any(keyword in error_str for keyword in ['quota', 'exhausted', '429']):
                            consecutive_quota_failures += 1
                            chat_logger.debug(f"Key {key_index+1} quota exhausted (consecutive: {consecutive_quota_failures})")
                            if key_index < len(all_keys) - 1:
                                # Try next key
                                break
                            else:
                                # Last key, raise quota error
                                from google.api_core.exceptions import ResourceExhausted
                                raise ResourceExhausted(f"All {len(all_keys)} API keys exhausted embedding quota")
                        
                        # Check if it's a rate limit (temporary)
                        elif any(keyword in error_str for keyword in ['rate limit', '503']):
                            if attempt < max_retries - 1:
                                wait_time = min(2.0 ** attempt, 5.0)
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                break  # Try next key
                        else:
                            # For other errors, raise immediately
                            raise error
                            
                except Exception as e:
                    # For non-embedding errors, raise immediately
                    raise
        
        # If we get here, all keys failed
        from google.api_core.exceptions import ResourceExhausted
        raise ResourceExhausted(f"Failed to generate embedding with {len(all_keys)} API keys")
    
    @staticmethod
    async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        tasks = [EmbeddingService.generate_embedding(text) for text in texts]
        embeddings = await asyncio.gather(*tasks, return_exceptions=True)
        
        result = []
        for i, emb in enumerate(embeddings):
            if isinstance(emb, Exception):
                chat_logger.error(f"Failed to generate embedding for text {i}", error=str(emb))
                raise emb
            result.append(emb)
        
        return result
    
    @staticmethod
    async def generate_query_embedding(query: str, max_retries: int = 1) -> List[float]:
        """
        Generate embedding for a query text with multi-key fallback
        
        REDUCED RETRIES: Only 1 retry per key to prevent quota exhaustion
        Stops early if 5+ consecutive keys fail with quota errors
        """
        loop = asyncio.get_event_loop()
        
        # Get all available API keys for fallback
        all_keys = EmbeddingService.get_all_api_keys()
        quota_errors = []
        
        # Try each key once
        for key_index, api_key in enumerate(all_keys):
            for attempt in range(max_retries):
                def _generate():
                    try:
                        chat_logger.debug(f"Using API key {key_index + 1}/{len(all_keys)}: {api_key[:20]}...")
                        genai.configure(api_key=api_key)
                        
                        # Truncate query if too long (max 2048 tokens ~= 8000 chars)
                        query_truncated = query[:8000] if len(query) > 8000 else query
                        
                        chat_logger.debug(f"Calling embed_content with query length: {len(query_truncated)}")
                        result = genai.embed_content(
                            model="models/embedding-001",
                            content=query_truncated,
                            task_type="retrieval_query"
                        )
                        chat_logger.debug("Embedding generated successfully")
                        return result['embedding'], None
                    except Exception as e:
                        # Log the actual error details
                        error_type = type(e).__name__
                        chat_logger.error("Query embedding generation error", 
                                        error=str(e), 
                                        error_type=error_type,
                                        api_key_index=key_index + 1,
                                        attempt=attempt + 1)
                        return None, e
                
                try:
                    embedding, error = await loop.run_in_executor(embedding_pool, _generate)
                    
                    if embedding:
                        chat_logger.info("Query embedding generated successfully", 
                                       embedding_dim=len(embedding),
                                       api_key_index=key_index + 1)
                        return embedding
                    
                    if error:
                        error_str = str(error).lower()
                        
                        # Check if it's a quota error
                        if any(keyword in error_str for keyword in ['quota', 'exhausted', '429']):
                            quota_errors.append(f"Key {key_index + 1}: {str(error)[:100]}")
                            chat_logger.warning(f"Quota exhausted for key {key_index + 1}/{len(all_keys)}, trying next key")
                            break  # Try next key
                        
                        # Check if it's a rate limit (temporary)
                        elif any(keyword in error_str for keyword in ['rate limit', '503']):
                            if attempt < max_retries - 1:
                                wait_time = min(2.0 ** attempt, 5.0)
                                chat_logger.info(f"Rate limit hit, waiting {wait_time}s before retry")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                # Move to next key after retries
                                break
                        else:
                            # For other errors, raise immediately
                            raise error
                            
                except Exception as e:
                    # For non-embedding errors, raise immediately
                    chat_logger.error("Unexpected error in embedding generation", 
                                    error=str(e),
                                    error_type=type(e).__name__)
                    raise
        
        # If we get here, all keys failed with quota errors
        error_msg = f"All {len(all_keys)} API keys have exhausted their embedding quota. " \
                   f"Please upgrade your API plan or wait for quota reset. " \
                   f"Learn more: https://ai.google.dev/gemini-api/docs/rate-limits"
        chat_logger.error("All API keys exhausted", 
                        num_keys_tried=len(all_keys),
                        sample_errors=quota_errors[:3])
        
        # Raise a specific exception for quota exhaustion
        from google.api_core.exceptions import ResourceExhausted
        raise ResourceExhausted(error_msg)
