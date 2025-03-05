from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Union
import logging

class CustomCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for logging LLM interactions"""
    
    def __init__(self):
        """Initialize custom callback handler"""
        super().__init__()
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='llm_detailed_logs.txt'
        )
        self.logger = logging.getLogger("LLM_Logger")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Log when LLM starts running"""
        self.logger.info(f"\n🚀 LLM Start\nPrompts: {prompts}")

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Log when LLM ends running"""
        self.logger.info(f"\n✅ LLM Response\nOutput: {response}")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Log when LLM errors"""
        self.logger.error(f"\n❌ LLM Error\nError: {error}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Log when chain starts running"""
        self.logger.info(f"\n🔗 Chain Start\nInputs: {inputs}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Log when chain ends running"""
        self.logger.info(f"\n🔗 Chain End\nOutputs: {outputs}") 