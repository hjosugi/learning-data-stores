"""Unit tests for the embedded vector store.

Run non-interactively; exits non-zero on any failure:

    python3 projects/vector-search-lab/test_app.py
"""

from __future__ import annotations

import unittest

from app import (
    EMBED_DIM,
    VectorStore,
    build_sample_store,
    cosine_similarity,
    embed,
    has_category,
    keyword_overlap,
)


class TestEmbedding(unittest.TestCase):
    def test_embedding_is_deterministic(self) -> None:
        # Same text must always produce the same vector (process-stable hash).
        self.assertEqual(embed("hello world"), embed("hello world"))

    def test_embedding_is_unit_length(self) -> None:
        vector = embed("vector databases store embeddings")
        norm = sum(component * component for component in vector) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=9)

    def test_empty_text_is_zero_vector(self) -> None:
        self.assertEqual(embed(""), [0.0] * EMBED_DIM)

    def test_cosine_of_identical_text_is_one(self) -> None:
        vector = embed("lions and tigers")
        self.assertAlmostEqual(cosine_similarity(vector, vector), 1.0, places=9)


class TestNearestNeighbour(unittest.TestCase):
    def test_ordering_is_sensible(self) -> None:
        # A query about programming should rank the programming docs above the
        # animal/coffee docs under pure dense (cosine) search.
        store = build_sample_store()
        hits = store.search("programming language", k=6, hybrid_alpha=1.0)
        ranked_ids = [hit.id for hit in hits]
        self.assertIn(ranked_ids[0], {"doc-3", "doc-4"})
        # The programming docs must outrank the coffee doc.
        self.assertLess(ranked_ids.index("doc-3"), ranked_ids.index("doc-6"))
        self.assertLess(ranked_ids.index("doc-4"), ranked_ids.index("doc-6"))

    def test_scores_are_descending(self) -> None:
        store = build_sample_store()
        hits = store.search("wild big cats", k=6)
        scores = [hit.score for hit in hits]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestMetadataFilter(unittest.TestCase):
    def test_filter_excludes_other_categories(self) -> None:
        store = build_sample_store()
        hits = store.search("anything", k=6, metadata_filter=has_category("food"))
        returned_ids = {hit.id for hit in hits}
        # Only the single 'food' document may appear.
        self.assertEqual(returned_ids, {"doc-6"})

    def test_filter_predicate_on_tags(self) -> None:
        store = build_sample_store()
        hits = store.search(
            "programming",
            k=6,
            metadata_filter=lambda metadata: "code" in metadata.get("tags", []),
        )
        returned_ids = {hit.id for hit in hits}
        self.assertEqual(returned_ids, {"doc-3", "doc-4"})

    def test_empty_filter_result(self) -> None:
        store = build_sample_store()
        hits = store.search("x", k=6, metadata_filter=has_category("does-not-exist"))
        self.assertEqual(hits, [])


class TestUpsertDelete(unittest.TestCase):
    def test_upsert_overwrites_in_place(self) -> None:
        store = VectorStore()
        store.upsert("a", "first version", {"category": "x"})
        self.assertEqual(len(store), 1)
        store.upsert("a", "second version", {"category": "y"})
        self.assertEqual(len(store), 1)  # same id -> overwrite, not append
        document = store.get("a")
        self.assertEqual(document.text, "second version")
        self.assertEqual(document.metadata["category"], "y")

    def test_delete_removes_document(self) -> None:
        store = build_sample_store()
        before = len(store)
        self.assertTrue(store.delete("doc-3"))
        self.assertEqual(len(store), before - 1)
        self.assertIsNone(store.get("doc-3"))
        # A deleted document can no longer be returned by search.
        hits = store.search("programming language", k=6, hybrid_alpha=1.0)
        self.assertNotIn("doc-3", {hit.id for hit in hits})

    def test_delete_missing_returns_false(self) -> None:
        store = build_sample_store()
        self.assertFalse(store.delete("nope"))


class TestHybridSearch(unittest.TestCase):
    def test_keyword_overlap_bounds(self) -> None:
        self.assertEqual(keyword_overlap("cats dogs", "cats dogs"), 1.0)
        self.assertEqual(keyword_overlap("cats", "coffee"), 0.0)
        self.assertEqual(keyword_overlap("", "anything"), 0.0)

    def test_hybrid_changes_ranking(self) -> None:
        # Craft a store where the exact keyword match (doc-kw) shares no hashed
        # buckets advantage over a semantically-padded doc (doc-dense) under
        # pure cosine, but wins once keyword overlap is mixed in.
        store = VectorStore()
        store.upsert("doc-kw", "alpha beta", {})
        store.upsert("doc-dense", "alpha alpha alpha gamma delta epsilon", {})

        dense_only = store.search("beta", k=2, hybrid_alpha=1.0)
        hybrid = store.search("beta", k=2, hybrid_alpha=0.0)

        # Under pure keyword search the exact match must rank first.
        self.assertEqual(hybrid[0].id, "doc-kw")
        # The keyword score for the exact-match doc is strictly positive.
        kw_hit = next(hit for hit in hybrid if hit.id == "doc-kw")
        self.assertGreater(kw_hit.keyword, 0.0)
        # And the blend weight genuinely changes the produced scores.
        dense_scores = {hit.id: hit.score for hit in dense_only}
        hybrid_scores = {hit.id: hit.score for hit in hybrid}
        self.assertNotEqual(dense_scores, hybrid_scores)

    def test_hybrid_reorders_versus_dense(self) -> None:
        # Demonstrate an actual ranking inversion between dense and keyword modes.
        #
        # d_long_tf repeats the query term 'alpha' many times inside a long
        # document: term-frequency concentration gives it the highest cosine,
        # but its large vocabulary gives it a low Jaccard keyword overlap.
        # d_short mentions 'alpha' once in a tiny document: lower cosine but
        # higher keyword overlap. So dense and keyword search disagree on rank 1.
        store = VectorStore()
        store.upsert("d_long_tf", "alpha alpha alpha bravo charlie delta echo foxtrot golf hotel", {})
        store.upsert("d_short", "alpha xray", {})

        dense = [hit.id for hit in store.search("alpha", k=2, hybrid_alpha=1.0)]
        keyword = [hit.id for hit in store.search("alpha", k=2, hybrid_alpha=0.0)]
        self.assertEqual(dense[0], "d_long_tf")
        self.assertEqual(keyword[0], "d_short")
        # The two strategies produce different orderings.
        self.assertNotEqual(dense, keyword)


if __name__ == "__main__":
    unittest.main(verbosity=2)
