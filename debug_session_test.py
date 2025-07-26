import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from unittest.mock import patch
import browse_to_test as btt
from browse_to_test.ai.base import AIResponse, AIProviderError

class DebugMockProvider:
    def __init__(self):
        self.call_count = 0
    
    def generate(self, prompt, system_prompt=None, **kwargs):
        self.call_count += 1
        return AIResponse(
            content="test script content",
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=150
        )
    
    async def generate_async(self, prompt, system_prompt=None, **kwargs):
        self.call_count += 1
        await asyncio.sleep(0.1)
        return AIResponse(
            content="test script content",
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=150
        )
    
    async def analyze_with_context_async(self, request, **kwargs):
        self.call_count += 1
        await asyncio.sleep(0.1)
        return AIResponse(
            content="analysis complete",
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=150
        )

async def test_simple_session():
    provider = DebugMockProvider()
    
    step = {
        "model_output": {
            "action": [{"click": {"selector": "#button"}}]
        },
        "metadata": {"step_description": "Click button"}
    }
    
    with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
        session = btt.AsyncIncrementalSession(
            btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
        )
        
        try:
            await session.start()
            print("Session started successfully")
            
            # Add one step
            result = await session.add_step_async(step, wait_for_completion=False)
            print(f"Step queued: {result.success}, task_id: {result.metadata.get('task_id')}")
            
            # Wait for it with longer timeout
            task_id = result.metadata['task_id']
            final_result = await session.wait_for_task(task_id, timeout=10)
            print(f"Step completed: {final_result.success}")
            
            print(f"Provider calls: {provider.call_count}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                await session.finalize_async(wait_for_pending=False)
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_simple_session())
