"""Abstract interface for document loader implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncIterator, Iterator, List, Optional

from core.documents.base import Document

# from langchain_core.runnables import run_in_executor


if TYPE_CHECKING:
    from core.text_splitters.base import TextSplitter

from core.document_loaders.blob_loaders import Blob


class BaseLoader(ABC):
    """Interface for Document Loader.

    Implementations should implement the lazy-loading method using generators
    to avoid loading all Documents into memory at once.

    `load` is provided just for user convenience and should not be overridden.
    """

    # Sub-classes should not implement this method directly. Instead, they
    # should implement the lazy load method.
    def load(self) -> List[Document]:
        """Load data into Document objects."""
        return list(self.lazy_load())

    def load_and_split(
        self, text_splitter: Optional[TextSplitter] = None
    ) -> List[Document]:
        """Load Documents and split into chunks. Chunks are returned as Documents.

        Do not override this method. It should be considered to be deprecated!

        Args:
            text_splitter: TextSplitter instance to use for splitting documents.
              Defaults to RecursiveCharacterTextSplitter.

        Returns:
            List of Documents.
        """

        if text_splitter is None:
            try:
                from core.text_splitters.character import RecursiveCharacterTextSplitter
            except ImportError as e:
                raise ImportError(
                    "Unable to import from text_splitters. Please specify "
                    "text_splitter or install langchain_text_splitters with "
                    "`pip install -U langchain-text-splitters`."
                ) from e

            _text_splitter: TextSplitter = RecursiveCharacterTextSplitter()
        else:
            _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs)

    # Attention: This method will be upgraded into an abstractmethod once it's
    #            implemented in all the existing subclasses.
    def lazy_load(self) -> Iterator[Document]:
        """A lazy loader for Documents."""
        if type(self).load != BaseLoader.load:
            return iter(self.load())
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement lazy_load()"
        )

    async def alazy_load(self) -> AsyncIterator[Document]:
        """A lazy loader for Documents."""
        #iterator = await run_in_executor(None, self.lazy_load)
        done = object()
        while True:
            doc = await run_in_executor(None, next, iterator, done)  # type: ignore[call-arg, arg-type]
            if doc is done:
                break
            yield doc  # type: ignore[misc]

