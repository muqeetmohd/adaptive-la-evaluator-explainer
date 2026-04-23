import random
from knowledge_base.embed import load_knowledge_base


def inspect_knowledge_base(persist_dir: str = "./chroma_db"):
    collection = load_knowledge_base(persist_dir)

    total = collection.count()
    print(f"\nTotal chunks: {total}\n")

    all_data = collection.get(include=["metadatas", "documents"])
    metadatas = all_data["metadatas"]
    documents = all_data["documents"]

    tier_counts = {1: 0, 2: 0, 3: 0}
    source_counts = {}
    topic_counts = {}

    for m in metadatas:
        tier_counts[m["tier"]] = tier_counts.get(m["tier"], 0) + 1
        source_counts[m["source"]] = source_counts.get(m["source"], 0) + 1
        topic_counts[m["topic"]] = topic_counts.get(m["topic"], 0) + 1

    print("Chunks by tier:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  Tier {tier}: {count}")

    print("\nChunks by source:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")

    print("\nChunks by topic:")
    for topic, count in sorted(topic_counts.items()):
        print(f"  {topic}: {count}")

    print("\n--- Sample chunks (3 per tier) ---")
    for tier in [1, 2, 3]:
        indices = [i for i, m in enumerate(metadatas) if m["tier"] == tier]
        sample = random.sample(indices, min(3, len(indices)))
        print(f"\nTier {tier} samples:")
        for idx in sample:
            m = metadatas[idx]
            print(f"  [source={m['source']} topic={m['topic']}]")
            print(f"  {documents[idx][:200]}")
            print()


if __name__ == "__main__":
    inspect_knowledge_base()
