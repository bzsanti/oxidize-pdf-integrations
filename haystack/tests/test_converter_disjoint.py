"""Semantic regression tests for ``OxidizePdfConverter(mode='rag')``.

These tests verify the chunks emitted are **element-disjoint** — no
``Document``'s ``content`` is a substring of another's, and each unique
source marker appears in exactly one ``Document``.

Background: the sibling ``llama-index-readers-oxidize-pdf`` 0.1.0 was
published with shape-only tests that missed a quadratic accumulation
bug in ``HybridChunker`` (oxidize-pdf-core 2.5.4). This file exists so
the same gap cannot recur in the Haystack converter. Failure here =
either the bridge regressed or the converter stopped propagating the
chunker's output verbatim. Either is a release blocker.
"""

from __future__ import annotations

import pathlib

import pytest

import oxidize_pdf as op
from haystack_oxidize_pdf import OxidizePdfConverter


_TITLE_MARKER = "HEAD-ALPHA-XYZ"
_PARA_MARKERS = (
    "para-alpha-marker-q1",
    "para-bravo-marker-q2",
    "para-charlie-marker-q3",
)


@pytest.fixture
def disjointness_pdf(tmp_path: pathlib.Path) -> pathlib.Path:
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


def _assert_documents_pairwise_disjoint(docs) -> None:
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            ti, tj = docs[i].content, docs[j].content
            assert ti, f"docs[{i}].content is empty"
            assert tj, f"docs[{j}].content is empty"
            assert ti not in tj, (
                f"docs[{i}].content is a substring of docs[{j}].content — "
                f"quadratic accumulation bug regressed.\n"
                f"  i={ti!r}\n  j={tj!r}"
            )
            assert tj not in ti, (
                f"docs[{j}].content is a substring of docs[{i}].content — "
                f"quadratic accumulation bug regressed.\n"
                f"  i={ti!r}\n  j={tj!r}"
            )


def _assert_marker_appears_exactly_once(docs, marker: str) -> None:
    occurrences = sum(1 for d in docs if marker in d.content)
    assert occurrences == 1, (
        f"marker {marker!r} must appear in exactly one Document; "
        f"found in {occurrences}.\n"
        f"  texts: {[d.content for d in docs]}"
    )


class TestRagModeChunkDisjointness:
    def test_title_plus_paragraphs_documents_are_disjoint(
        self, disjointness_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[disjointness_pdf])[
            "documents"
        ]
        assert len(docs) > 0
        _assert_documents_pairwise_disjoint(docs)

    def test_each_paragraph_marker_appears_exactly_once(
        self, disjointness_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[disjointness_pdf])[
            "documents"
        ]
        for marker in _PARA_MARKERS:
            _assert_marker_appears_exactly_once(docs, marker)

    def test_chunk_count_bounded_by_source_elements(
        self, disjointness_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[disjointness_pdf])[
            "documents"
        ]
        assert len(docs) <= 4, (
            f"document count ({len(docs)}) exceeds 4 source elements; "
            "duplication suspected"
        )

    def test_multi_section_documents_are_disjoint(
        self, multi_section_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[multi_section_pdf])[
            "documents"
        ]
        assert len(docs) > 0
        _assert_documents_pairwise_disjoint(docs)

    def test_multi_section_each_marker_appears_exactly_once(
        self, multi_section_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[multi_section_pdf])[
            "documents"
        ]

        for section_idx in range(2):
            for para_idx in range(3):
                marker = f"sec{section_idx}-para{para_idx}-token-zzz"
                _assert_marker_appears_exactly_once(docs, marker)

    def test_multi_section_count_bounded(self, multi_section_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="rag").run(sources=[multi_section_pdf])[
            "documents"
        ]
        assert len(docs) <= 8, (
            f"document count ({len(docs)}) exceeds 8 source elements; "
            "duplication suspected"
        )
