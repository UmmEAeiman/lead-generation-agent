from app.integrations.llm.embeddings import cosine_similarity, embed_text


def test_embedding_is_deterministic_and_normalized() -> None:
    a = embed_text("dental clinic in Texas")
    b = embed_text("dental clinic in Texas")
    assert a == b
    assert len(a) == 1024
    magnitude = sum(v * v for v in a) ** 0.5
    assert abs(magnitude - 1.0) < 1e-5


def test_similar_text_scores_higher() -> None:
    base = "dental clinic booking software"
    similar = "software for dental clinic bookings"
    unrelated = "freight logistics shipping container"
    base_v = embed_text(base)
    assert cosine_similarity(base_v, embed_text(similar)) > cosine_similarity(
        base_v, embed_text(unrelated)
    )


def test_empty_text_embedding_is_zero_vector() -> None:
    vector = embed_text("")
    assert all(v == 0.0 for v in vector)
    assert cosine_similarity(vector, embed_text("anything")) == 0.0
