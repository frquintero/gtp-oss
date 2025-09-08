"""Analysis Manager for handling different thinking modes."""
from typing import Dict, Any, Optional, Callable
from .prompt_engine import PromptEngine


class AnalysisManager:
    """Manager for different analysis modes (normal vs hard thinking)."""

    def __init__(self, groq_client: Any, prompt_engine: PromptEngine):
        self.groq_client = groq_client
        self.prompt_engine = prompt_engine

    def perform_analysis(
        self,
        question: str,
        mode: str = 'normal',
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """Perform analysis based on the selected mode."""
        if mode == 'hard':
            return self.perform_deep_analysis(question, progress_callback)
        else:
            return self.perform_normal_analysis(question)

    def perform_normal_analysis(self, question: str) -> str:
        """Perform normal analysis (current behavior)."""
        # Use the groq client directly for normal mode with streaming
        try:
            messages = [{"role": "user", "content": question}]
            
            # Get model from config
            if hasattr(self.groq_client, 'config') and self.groq_client.config:
                model = self.groq_client.config.get('default_model', 'openai/gpt-oss-20b')
            else:
                model = 'openai/gpt-oss-20b'
            
            # Use streaming and collect full response
            full_response = ""
            stream = self.groq_client.create_completion(
                messages=messages,
                model=model,
                stream=True,
                max_completion_tokens=4096,
                temperature=0.8
            )
            
            # Collect all chunks
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta:
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
            
            if full_response.strip():
                return full_response.strip()
            else:
                return "Error: No response content received from API"
                
        except Exception as e:
            return f"Error in normal analysis: {str(e)}"

    def perform_deep_analysis(
        self,
        question: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """Perform deep analysis using the 8-step optimized sequence."""
        try:
            # Execute the complete sequence
            responses = self.prompt_engine.execute_optimized_sequence(
                question,
                self.groq_client,
                progress_callback
            )

            # Return the final response (step 8)
            final_response = responses.get(8, "Error: No final response generated")

            # Optionally include intermediate steps for debugging
            if self._should_include_intermediates():
                return self._format_complete_response(responses)
            else:
                return final_response

        except Exception as e:
            error_msg = f"Error in deep analysis: {str(e)}"
            return error_msg

    def _should_include_intermediates(self) -> bool:
        """Check if intermediate responses should be included."""
        # This could be configurable
        return False

    def _format_complete_response(self, responses: Dict[int, str]) -> str:
        """Format the complete response including all steps."""
        formatted = "🔍 **Deep Analysis Results**\n\n"

        for step in range(1, 9):
            step_info = self.prompt_engine.prompts.get(step, {})
            step_name = step_info.get("name", f"Step {step}")
            response = responses.get(step, "No response")

            formatted += f"**{step}. {step_name}:**\n{response}\n\n"

        return formatted

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about the analysis process."""
        return {
            "total_steps": 8,
            "completed_steps": len(self.prompt_engine.get_state()),
            "current_mode": "normal"  # This will be updated when integrated
        }