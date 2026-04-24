"""
Run this script once after placing the 4 synthetic note PDFs in data/raw/ to build the knowledge base.
Usage: python build_kb.py
"""
from knowledge_base.parse import parse_all_sources
from knowledge_base.chunk import chunk_all_sources, assign_topics
from knowledge_base.embed import build_knowledge_base

print("Step 1: Parsing PDFs...")
parsed = parse_all_sources()
for source, pages in parsed.items():
    print(f"  {source}: {len(pages)} pages")

print("\nStep 2: Chunking...")
chunks = chunk_all_sources(parsed)
print(f"  Total chunks before topic assignment: {len(chunks)}")

print("\nStep 3: Assigning topics...")
chunks = assign_topics(chunks)

topic_counts = {}
for c in chunks:
    topic_counts[c["topic"]] = topic_counts.get(c["topic"], 0) + 1
for topic, count in sorted(topic_counts.items()):
    print(f"  {topic}: {count}")

print("\nStep 4: Embedding and ingesting into ChromaDB...")
build_knowledge_base(chunks)

print("\nKnowledge base build complete.")
print("Run `python knowledge_base/inspect.py` to verify chunk quality.")
