"""Prompt Engine for optimized thinking sequence."""
from typing import Dict, Any, List, Callable, Optional
from .prompt_templates import get_prompt_template, PROMPT_TEMPLATES


class PromptEngine:
    """Engine for executing optimized prompt sequences."""

    def __init__(self, groq_client: Any):
        self.groq_client = groq_client
        self.prompts = PROMPT_TEMPLATES
        self.state = {}

    def _load_prompt_templates(self) -> Dict[int, Dict[str, str]]:
        """Load all prompt templates."""
        return self.prompts

    def execute_single_prompt(
        self,
        step_number: int,
        user_question: str,
        previous_responses: Dict[int, str],
        groq_client: Any = None
    ) -> str:
        """Execute a single prompt in the sequence."""
        template = get_prompt_template(step_number)
        if not template:
            raise ValueError(f"No template found for step {step_number}")

        # Build the prompt by replacing placeholders
        prompt = template["template"].format(
            user_question=user_question,
            response_1=previous_responses.get(1, ""),
            response_2=previous_responses.get(2, ""),
            response_3=previous_responses.get(3, ""),
            response_4=previous_responses.get(4, ""),
            response_5=previous_responses.get(5, ""),
            response_6=previous_responses.get(6, ""),
            response_7=previous_responses.get(7, "")
        )

        # Execute the prompt using groq_client
        client = groq_client or self.groq_client
        response = self._execute_prompt_with_client(prompt, client)

        # Store the response in state
        self.state[step_number] = response

        return response

    def execute_optimized_sequence(
        self,
        user_question: str,
        groq_client: Any,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[int, str]:
        """Execute the complete 8-step optimized sequence."""
        responses = {}

        for step in range(1, 9):  # Steps 1-8
            if progress_callback:
                step_info = get_prompt_template(step)
                progress_callback(step, step_info.get("name", f"Step {step}"))

            try:
                response = self.execute_single_prompt(
                    step, user_question, responses, groq_client
                )
                responses[step] = response

            except Exception as e:
                # Handle errors gracefully - could implement retry logic here
                error_msg = f"Error in step {step}: {str(e)}"
                responses[step] = error_msg
                if progress_callback:
                    progress_callback(step, f"Error: {error_msg}")

        return responses

    def _execute_prompt_with_client(self, prompt: str, groq_client: Any) -> str:
        """Execute a prompt using the Groq client."""
        try:
            # Create messages for the API call
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Get the default model from the client's config
            if hasattr(groq_client, 'config') and groq_client.config:
                model = groq_client.config.get('default_model', 'openai/gpt-oss-20b')
            else:
                model = 'openai/gpt-oss-20b'
            
            # Use streaming to collect the full response
            full_response = ""
            
            # Create streaming completion
            stream = groq_client.create_completion(
                messages=messages,
                model=model,
                stream=True,
                max_completion_tokens=2048,
                temperature=0.7
            )
            
            # Collect all chunks into a full response
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
            return f"Error executing prompt: {str(e)}"

    def get_state(self) -> Dict[int, str]:
        """Get current state of responses."""
        return self.state.copy()

    def reset_state(self) -> None:
        """Reset the engine state."""
        self.state = {}