"""LLM-based classifier interface."""

from abc import abstractmethod
from typing import Generic, TypeVar

from workflow_engine.workflows.base.event import BaseEventType
from workflow_engine.workflows.classifiers.base import AbstractClassifier

E = TypeVar("E", bound=BaseEventType)


class LLMClassifier(AbstractClassifier[E], Generic[E]):
    """LLM-based classifier interface.

    This is a stub/interface for LLM-based classification.
    Concrete implementations would integrate with providers like
    OpenAI, Anthropic, or other LLM services.

    Example implementation:
        class OpenAIClassifier(LLMClassifier[MyEventType]):
            async def classify_async(self, content: str) -> MyEventType | None:
                response = await openai_client.chat.completions.create(...)
                return self._parse_response(response)
    """

    def __init__(
        self,
        event_type_enum: type[E],
        prompt_template: str | None = None,
    ):
        """Initialize the LLM classifier.

        Args:
            event_type_enum: The enum class for valid event types
            prompt_template: Optional custom prompt template.
                            Should include {categories} and {content} placeholders.
        """
        self._event_type_enum = event_type_enum
        self._prompt_template = prompt_template or self._default_prompt_template()

    def _default_prompt_template(self) -> str:
        """Return the default prompt template."""
        return """Classify the following email content into one of these categories: {categories}

Email content:
{content}

Respond with only the category name, nothing else."""

    def _get_categories(self) -> list[str]:
        """Get list of category names from the event enum."""
        return [e.name for e in self._event_type_enum]

    def _build_prompt(self, content: str) -> str:
        """Build the classification prompt."""
        categories = ", ".join(self._get_categories())
        return self._prompt_template.format(categories=categories, content=content)

    def _parse_response(self, response: str) -> E | None:
        """Parse LLM response into an event type.

        Args:
            response: The raw response from the LLM

        Returns:
            The matching event type, or None if no match
        """
        response_clean = response.strip().upper()
        for event in self._event_type_enum:
            if event.name.upper() == response_clean:
                return event
        return None

    def classify(self, content: str) -> E | None:
        """Sync classification - not recommended for LLM calls.

        Raises:
            NotImplementedError: LLM calls should use classify_async
        """
        raise NotImplementedError(
            "LLM-based classification requires async. Use classify_async instead."
        )

    @abstractmethod
    async def classify_async(self, content: str) -> E | None:
        """Implement this method to call your LLM provider.

        Example implementation:
            async def classify_async(self, content: str) -> E | None:
                prompt = self._build_prompt(content)
                response = await self._llm_client.complete(prompt)
                return self._parse_response(response)
        """
        pass
