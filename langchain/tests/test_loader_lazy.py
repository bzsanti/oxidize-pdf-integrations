"""Guard that ``lazy_load()`` actually lazy-loads.

LangChain's ``BaseLoader`` docstring is explicit: implementations
override ``lazy_load()`` (a generator); ``load()`` stays inherited as
the convenience materializer. If a future maintainer accidentally
returns a list from ``lazy_load()`` — or overrides ``load()`` — these
tests fail so the regression is caught before release.
"""

from __future__ import annotations

import pathlib
from types import GeneratorType

from langchain_core.documents import Document

from langchain_oxidize_pdf import OxidizePdfLoader


class TestLazyLoadSemantics:
    def test_lazy_load_returns_iterator_not_list(self, sample_pdf: pathlib.Path):
        result = OxidizePdfLoader(sample_pdf, mode="pages").lazy_load()

        # The LangChain contract says lazy_load returns Iterator[Document].
        # A generator satisfies Iterator; a list materialized eagerly does not.
        assert not isinstance(result, list), (
            "lazy_load() returned a list; it must return an iterator/generator "
            "so downstream consumers control materialization."
        )
        # Exercising the iterator protocol: iter(result) must succeed and
        # next(...) must produce a Document. If either fails, the contract
        # is broken regardless of the concrete type.
        iterator = iter(result)
        first = next(iterator)
        assert isinstance(first, Document)

    def test_lazy_load_yields_documents_with_content(self, sample_pdf: pathlib.Path):
        it = OxidizePdfLoader(sample_pdf, mode="pages").lazy_load()
        first = next(it)
        assert isinstance(first, Document)
        assert first.page_content

    def test_load_materializes_same_content_as_lazy_load(
        self, sample_pdf: pathlib.Path
    ):
        eager = OxidizePdfLoader(sample_pdf, mode="pages").load()
        lazy = list(OxidizePdfLoader(sample_pdf, mode="pages").lazy_load())

        assert len(eager) == len(lazy)
        for e, l in zip(eager, lazy):
            assert e.page_content == l.page_content
            assert e.metadata == l.metadata

    def test_lazy_load_across_all_modes(self, sample_pdf: pathlib.Path):
        # Every mode must respect the generator contract, not just pages.
        for mode in ("rag", "pages", "markdown"):
            result = OxidizePdfLoader(sample_pdf, mode=mode).lazy_load()
            assert not isinstance(result, list), (
                f"mode={mode!r}: lazy_load() returned a list; expected iterator."
            )
            # Draining must produce at least one document for a non-empty PDF.
            docs = list(result)
            assert len(docs) >= 1, f"mode={mode!r}: produced 0 documents"


class TestGeneratorIdentity:
    """Implementation-detail-ish but catches overrides that break laziness.

    If someone refactors and accidentally writes::

        def lazy_load(self):
            return self._load_rag(...)  # a list

    that would pass a naive "it's iterable" check but break memory
    guarantees for very large PDFs. Insisting on the ``generator`` type
    keeps the contract honest.
    """

    def test_lazy_load_is_a_generator(self, sample_pdf: pathlib.Path):
        result = OxidizePdfLoader(sample_pdf, mode="pages").lazy_load()
        assert isinstance(result, GeneratorType), (
            f"lazy_load() should return a generator; got {type(result).__name__}. "
            "Returning a list or other eager container violates BaseLoader's "
            "memory contract."
        )
