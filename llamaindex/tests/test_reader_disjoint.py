"""Semantic regression tests for ``OxidizePdfReader(mode='rag')``.

These tests verify the chunks emitted by the LlamaIndex ``Document`` list
are **element-disjoint** — no document's text is a substring of another's,
and each unique source marker appears in exactly one ``Document``.

Background: ``llama-index-readers-oxidize-pdf`` 0.1.0 was published with
shape-only tests that verified metadata fields existed but never inspected
the chunk content for accumulation. The underlying bridge bug
(oxidize-pdf-core 2.5.4 ``HybridChunker`` overlap branch re-injecting
flushed elements) made every chunk i+1 contain chunk i as a prefix,
rendering the reader unusable for RAG ingestion despite the metadata
shape looking healthy.

This file exists so the same gap cannot recur silently. Failure here =
either the bridge regressed or the reader stopped propagating the
chunker's output verbatim. Either is a release blocker.
"""

from __future__ import annotations

import pathlib

import pytest

import oxidize_pdf as op
from llama_index.readers.oxidize_pdf import OxidizePdfReader


# ── Synthetic fixture builder ────────────────────────────────────────────

# Markers are token-shaped strings unlikely to collide with framework
# punctuation, so substring checks are unambiguous.
_TITLE_MARKER = "HEAD-ALPHA-XYZ"
_PARA_MARKERS = (
    "para-alpha-marker-q1",
    "para-bravo-marker-q2",
    "para-charlie-marker-q3",
)


@pytest.fixture
def disjointness_pdf(tmp_path: pathlib.Path) -> pathlib.Path:
    """One-page PDF: 16pt bold title + three 11pt paragraphs.

    Mirrors the bridge's ``test_rag_chunks_disjoint`` and the core's
    ``end_to_end_pdf_produces_disjoint_chunks`` so a regression here is
    directly comparable to upstream test failures.
    """
    doc = op.Document()
    page = op.Page.a4()

    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, _TITLE_MARKER)

    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, f"Para1 body {_PARA_MARKERS[0]} ends.")
    page.text_at(50.0, 680.0, f"Para2 body {_PARA_MARKERS[1]} ends.")
    page.text_at(50.0, 660.0, f"Para3 body {_PARA_MARKERS[2]} ends.")

    doc.add_page(page)

    target = tmp_path / "disjoint.pdf"
    doc.save(str(target))
    return target


@pytest.fixture
def multi_section_pdf(tmp_path: pathlib.Path) -> pathlib.Path:
    """Two pages, each with a section title + three body paragraphs.

    Exercises the longer element stream where the 0.1.0 bug manifested
    most dramatically (each later chunk accumulated every prior chunk).
    """
    doc = op.Document()

    for section_idx, section_label in enumerate(("SECTION-ONE", "SECTION-TWO")):
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA_BOLD, 16.0)
        page.text_at(50.0, 750.0, section_label)
        page.set_font(op.Font.HELVETICA, 11.0)
        for para_idx in range(3):
            marker = f"sec{section_idx}-para{para_idx}-token-zzz"
            y = 700.0 - para_idx * 20.0
            page.text_at(50.0, y, f"Body line {marker} ends here.")
        doc.add_page(page)

    target = tmp_path / "multi.pdf"
    doc.save(str(target))
    return target


# ── Generic semantic assertions (mirror bridge test) ─────────────────────


def _assert_documents_pairwise_disjoint(docs) -> None:
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            ti, tj = docs[i].text, docs[j].text
            assert ti, f"docs[{i}].text is empty"
            assert tj, f"docs[{j}].text is empty"
            assert ti not in tj, (
                f"docs[{i}].text is a substring of docs[{j}].text — "
                f"quadratic accumulation bug regressed.\n"
                f"  i={ti!r}\n  j={tj!r}"
            )
            assert tj not in ti, (
                f"docs[{j}].text is a substring of docs[{i}].text — "
                f"quadratic accumulation bug regressed.\n"
                f"  i={ti!r}\n  j={tj!r}"
            )


def _assert_marker_appears_exactly_once(docs, marker: str) -> None:
    occurrences = sum(1 for d in docs if marker in d.text)
    assert occurrences == 1, (
        f"marker {marker!r} must appear in exactly one Document; "
        f"found in {occurrences}.\n"
        f"  texts: {[d.text for d in docs]}"
    )


# ── Tests ────────────────────────────────────────────────────────────────


class TestRagModeChunkDisjointness:
    """RAG-mode ``Document`` list must be element-disjoint."""

    def test_title_plus_paragraphs_documents_are_disjoint(
        self, disjointness_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="rag").load_data(disjointness_pdf)

        assert len(docs) > 0
        _assert_documents_pairwise_disjoint(docs)

    def test_each_paragraph_marker_appears_exactly_once(
        self, disjointness_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="rag").load_data(disjointness_pdf)
        for marker in _PARA_MARKERS:
            _assert_marker_appears_exactly_once(docs, marker)

    def test_chunk_count_bounded_by_source_elements(
        self, disjointness_pdf: pathlib.Path
    ):
        # Title + 3 paragraphs = 4 source elements. The chunker may merge
        # but MUST NOT split or duplicate, so 4 is the strict upper bound.
        docs = OxidizePdfReader(mode="rag").load_data(disjointness_pdf)
        assert len(docs) <= 4, (
            f"document count ({len(docs)}) exceeds 4 source elements; "
            "duplication suspected"
        )

    def test_multi_section_documents_are_disjoint(
        self, multi_section_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="rag").load_data(multi_section_pdf)

        assert len(docs) > 0
        _assert_documents_pairwise_disjoint(docs)

    def test_multi_section_each_marker_appears_exactly_once(
        self, multi_section_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="rag").load_data(multi_section_pdf)

        for section_idx in range(2):
            for para_idx in range(3):
                marker = f"sec{section_idx}-para{para_idx}-token-zzz"
                _assert_marker_appears_exactly_once(docs, marker)

    def test_multi_section_count_bounded(self, multi_section_pdf: pathlib.Path):
        # 2 sections * (1 title + 3 paragraphs) = 8 source elements.
        docs = OxidizePdfReader(mode="rag").load_data(multi_section_pdf)
        assert len(docs) <= 8, (
            f"document count ({len(docs)}) exceeds 8 source elements; "
            "duplication suspected"
        )

    def test_chunk_indexes_remain_sequential_under_disjointness(
        self, multi_section_pdf: pathlib.Path
    ):
        # Disjointness must not break sequential chunk_index numbering —
        # if the chunker drops/skips elements rather than overlapping, we
        # still want monotonic indices for downstream pipelines.
        docs = OxidizePdfReader(mode="rag").load_data(multi_section_pdf)
        indexes = [d.metadata["chunk_index"] for d in docs]
        assert indexes == list(range(len(docs)))
