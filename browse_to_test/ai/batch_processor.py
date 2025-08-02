"""
AI Batch Processor for optimizing multiple AI requests.

This module provides intelligent batching for AI requests to reduce API calls
and improve performance while maintaining context coherence.
"""

import asyncio
import hashlib
import json
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from .base import AIAnalysisRequest, AIResponse, AnalysisType

logger = logging.getLogger(__name__)


@dataclass
class BatchableRequest:
    """A request that can be batched with others."""

    id: str
    request: AIAnalysisRequest
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_batch_key(self) -> str:
        """Generate a key for grouping similar requests."""
        # Group by analysis type, framework, and target URL
        key_parts = [
            self.request.analysis_type.value,
            self.request.target_framework,
            self.request.target_url or "no_url"
        ]
        return "|".join(key_parts)
    
    def is_compatible_with(self, other: 'BatchableRequest') -> bool:
        """Check if this request can be batched with another."""
        # Same analysis type and framework
        if self.request.analysis_type != other.request.analysis_type:
            return False
        if self.request.target_framework != other.request.target_framework:
            return False
        
        # Same target URL (or both None)
        if self.request.target_url != other.request.target_url:
            return False
        
        # Compatible system context
        if bool(self.request.system_context) != bool(other.request.system_context):
            return False
        
        return True


@dataclass
class BatchResult:
    """Result of a batch AI request."""

    request_id: str
    response: Optional[AIResponse] = None
    error: Optional[Exception] = None
    extracted_content: Optional[str] = None


class AIBatchProcessor:
    """
    Intelligent batch processor for AI requests.
    
    Features:
    - Groups similar requests for batch processing
    - Reduces redundant API calls
    - Maintains context coherence
    - Supports priority-based processing
    """
    
    def __init__(
        self,
        max_batch_size: int = 5,
        batch_timeout: float = 0.5,  # seconds to wait for batch to fill
        cache_ttl: int = 3600  # 1 hour cache TTL
    ):
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout
        self.cache_ttl = cache_ttl
        
        # Request queues by batch key
        self._request_queues: Dict[str, List[BatchableRequest]] = defaultdict(list)
        self._processing_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        # Response cache
        self._response_cache: Dict[str, Tuple[AIResponse, datetime]] = {}
        self._cache_lock = asyncio.Lock()
        
        # Statistics
        self._stats = {
            'total_requests': 0,
            'batched_requests': 0,
            'cache_hits': 0,
            'api_calls_saved': 0
        }
    
    async def add_request(
        self,
        request_id: str,
        request: AIAnalysisRequest,
        priority: int = 0
    ) -> BatchableRequest:
        """Add a request to the batch queue."""
        batchable = BatchableRequest(
            id=request_id,
            request=request,
            priority=priority
        )
        
        batch_key = batchable.get_batch_key()
        self._request_queues[batch_key].append(batchable)
        self._stats['total_requests'] += 1
        
        logger.debug(f"Added request {request_id} to batch {batch_key}")
        return batchable
    
    async def process_batch(
        self,
        batch_key: str,
        ai_provider
    ) -> List[BatchResult]:
        """Process a batch of requests."""
        async with self._processing_locks[batch_key]:
            requests = self._request_queues[batch_key]
            if not requests:
                return []
            
            # Sort by priority (highest first)
            requests.sort(key=lambda r: r.priority, reverse=True)
            
            # Take up to max_batch_size requests
            batch = requests[:self.max_batch_size]
            self._request_queues[batch_key] = requests[self.max_batch_size:]
            
            # Check cache for each request
            results = []
            uncached_requests = []
            
            for req in batch:
                cached_response = await self._check_cache(req)
                if cached_response:
                    results.append(BatchResult(
                        request_id=req.id,
                        response=cached_response
                    ))
                    self._stats['cache_hits'] += 1
                else:
                    uncached_requests.append(req)
            
            # Process uncached requests
            if uncached_requests:
                try:
                    # Create combined prompt for batch
                    combined_response = await self._process_combined_requests(
                        uncached_requests,
                        ai_provider
                    )
                    
                    # Extract individual responses
                    extracted_results = self._extract_individual_responses(
                        uncached_requests,
                        combined_response
                    )
                    
                    # Cache responses
                    for req, result in zip(uncached_requests, extracted_results):
                        await self._cache_response(req, result.response)
                    
                    results.extend(extracted_results)
                    
                    # Update statistics
                    if len(uncached_requests) > 1:
                        self._stats['batched_requests'] += len(uncached_requests)
                        self._stats['api_calls_saved'] += len(uncached_requests) - 1
                    
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
                    # Create error results for all uncached requests
                    for req in uncached_requests:
                        results.append(BatchResult(
                            request_id=req.id,
                            error=e
                        ))
            
            return results
    
    async def wait_for_batch_or_timeout(
        self,
        batch_key: str,
        target_size: int = None
    ) -> bool:
        """Wait for batch to reach target size or timeout."""
        target_size = target_size or self.max_batch_size
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < self.batch_timeout:
            if len(self._request_queues[batch_key]) >= target_size:
                return True
            await asyncio.sleep(0.1)
        
        return False
    
    async def _process_combined_requests(
        self,
        requests: List[BatchableRequest],
        ai_provider
    ) -> AIResponse:
        """Process multiple requests in a single AI call."""
        # Create a combined analysis request
        combined_request = self._create_combined_request(requests)
        
        # Add batch processing instructions to system prompt
        system_prompt = self._generate_batch_system_prompt(combined_request)
        
        # Generate response
        response = await ai_provider.analyze_with_context_async(
            combined_request,
            system_prompt=system_prompt
        )
        
        # Add batch metadata
        response.metadata['batch_size'] = len(requests)
        response.metadata['request_ids'] = [r.id for r in requests]
        
        return response
    
    def _create_combined_request(
        self,
        requests: List[BatchableRequest]
    ) -> AIAnalysisRequest:
        """Create a combined request from multiple requests."""
        if not requests:
            raise ValueError("No requests to combine")
        
        # Use the first request as base
        base_request = requests[0].request
        
        # Combine automation data from all requests
        combined_automation_data = []
        for i, req in enumerate(requests):
            # Add section marker
            combined_automation_data.append({
                'section_id': f"request_{req.id}",
                'section_index': i,
                'automation_data': req.request.automation_data
            })
        
        # Create combined request
        combined = AIAnalysisRequest(
            analysis_type=base_request.analysis_type,
            automation_data=combined_automation_data,
            target_framework=base_request.target_framework,
            system_context=base_request.system_context,
            target_url=base_request.target_url,
            additional_context={
                'batch_processing': True,
                'batch_size': len(requests),
                'request_ids': [r.id for r in requests]
            }
        )
        
        return combined
    
    def _generate_batch_system_prompt(self, request: AIAnalysisRequest) -> str:
        """Generate system prompt for batch processing."""
        base_prompt = f"""You are processing multiple related automation sequences in a batch.

IMPORTANT: Structure your response with clear sections for each request.
Use the following format:

### Request: [request_id]
[Your analysis for this specific request]

### Request: [next_request_id]
[Your analysis for the next request]

Analyze each automation sequence independently while leveraging common patterns and insights across the batch. This improves efficiency while maintaining accuracy for each individual request.

Target Framework: {request.target_framework}
Analysis Type: {request.analysis_type.value}
"""
        return base_prompt
    
    def _extract_individual_responses(
        self,
        requests: List[BatchableRequest],
        combined_response: AIResponse
    ) -> List[BatchResult]:
        """Extract individual responses from combined AI response."""
        results = []
        content = combined_response.content
        
        # Try to split by request markers
        sections = self._split_response_sections(content)
        
        for i, req in enumerate(requests):
            # Find section for this request
            section_content = None
            
            # Look for exact request ID match
            for section_id, section_text in sections.items():
                if req.id in section_id or f"request_{req.id}" in section_id:
                    section_content = section_text
                    break
            
            # Fallback to index-based matching
            if not section_content and i < len(sections):
                section_keys = list(sections.keys())
                if i < len(section_keys):
                    section_content = sections[section_keys[i]]
            
            # Create individual response
            if section_content:
                individual_response = AIResponse(
                    content=section_content,
                    model=combined_response.model,
                    provider=combined_response.provider,
                    tokens_used=combined_response.tokens_used // len(requests) if combined_response.tokens_used else None,
                    metadata={
                        **combined_response.metadata,
                        'extracted_from_batch': True,
                        'batch_request_id': req.id
                    }
                )
                results.append(BatchResult(
                    request_id=req.id,
                    response=individual_response,
                    extracted_content=section_content
                ))
            else:
                # Couldn't extract specific section, use full response
                logger.warning(f"Could not extract section for request {req.id}")
                results.append(BatchResult(
                    request_id=req.id,
                    response=combined_response,
                    error=ValueError("Could not extract individual response from batch")
                ))
        
        return results
    
    def _split_response_sections(self, content: str) -> Dict[str, str]:
        """Split response content into sections by request markers."""
        sections = {}
        
        # Look for ### Request: markers
        import re
        pattern = r'###\s*Request:\s*([^\n]+)'
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            request_id = match.group(1).strip()
            start = match.end()
            
            # Find end of section (next marker or end of content)
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(content)
            
            section_content = content[start:end].strip()
            sections[request_id] = section_content
        
        # If no sections found, treat entire content as one section
        if not sections:
            sections['full_response'] = content
        
        return sections
    
    async def _check_cache(self, request: BatchableRequest) -> Optional[AIResponse]:
        """Check if we have a cached response for this request."""
        cache_key = self._generate_cache_key(request)
        
        async with self._cache_lock:
            if cache_key in self._response_cache:
                response, timestamp = self._response_cache[cache_key]
                
                # Check if cache is still valid
                if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                    logger.debug(f"Cache hit for request {request.id}")
                    return response
                else:
                    # Cache expired
                    del self._response_cache[cache_key]
        
        return None
    
    async def _cache_response(
        self,
        request: BatchableRequest,
        response: Optional[AIResponse]
    ):
        """Cache a response for future use."""
        if not response:
            return
        
        cache_key = self._generate_cache_key(request)
        
        async with self._cache_lock:
            self._response_cache[cache_key] = (response, datetime.now())
            
            # Clean up old cache entries
            await self._cleanup_cache()
    
    async def _cleanup_cache(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = []
        
        for key, (_, timestamp) in self._response_cache.items():
            if (now - timestamp).total_seconds() > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._response_cache[key]
    
    def _generate_cache_key(self, request: BatchableRequest) -> str:
        """Generate a cache key for a request."""
        # Create a hashable representation of the request
        key_data = {
            'analysis_type': request.request.analysis_type.value,
            'framework': request.request.target_framework,
            'target_url': request.request.target_url,
            'automation_data': json.dumps(
                request.request.automation_data,
                sort_keys=True
            )
        }
        
        # Add system context fingerprint if available
        if request.request.system_context:
            # Create a simple fingerprint of the context
            context_fingerprint = self._create_context_fingerprint(
                request.request.system_context
            )
            key_data['context_fingerprint'] = context_fingerprint
        
        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _create_context_fingerprint(self, context: Any) -> str:
        """Create a fingerprint of the system context for caching."""
        fingerprint_parts = []
        
        # Add project info
        if hasattr(context, 'project'):
            project = context.project
            if hasattr(project, 'name'):
                fingerprint_parts.append(f"project:{project.name}")
            if hasattr(project, 'test_frameworks'):
                fingerprint_parts.append(f"frameworks:{','.join(project.test_frameworks)}")
        
        # Add test count
        if hasattr(context, 'existing_tests'):
            fingerprint_parts.append(f"tests:{len(context.existing_tests)}")
        
        # Add UI component count
        if hasattr(context, 'ui_components'):
            fingerprint_parts.append(f"components:{len(context.ui_components)}")
        
        return "|".join(fingerprint_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get batch processor statistics."""
        return {
            **self._stats,
            'cache_size': len(self._response_cache),
            'active_batches': len(self._request_queues),
            'pending_requests': sum(len(q) for q in self._request_queues.values())
        }