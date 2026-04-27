import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from fitness.rag import _get_collection


class Command(BaseCommand):
    help = "Ingest curated wellness snippets into Chroma for Smart Coach RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/rag/sources.jsonl",
            help="Path to JSONL source file with source_id and text fields.",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "RAG_ENABLED", True):
            raise CommandError("RAG is disabled. Set RAG_ENABLED=True before ingestion.")

        src_path = Path(options["file"])
        if not src_path.is_absolute():
            src_path = Path(settings.BASE_DIR) / src_path
        if not src_path.exists():
            raise CommandError(f"Source file not found: {src_path}")

        entries = []
        with src_path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise CommandError(f"Invalid JSON on line {line_no}: {exc}") from exc
                source_id = str(item.get("source_id", "")).strip()
                text = str(item.get("text", "")).strip()
                if not source_id or not text:
                    raise CommandError(
                        f"Line {line_no} must include non-empty source_id and text."
                    )
                entries.append((source_id, text))

        if not entries:
            raise CommandError("No valid entries found in source file.")

        collection = _get_collection()
        ids = [f"{source_id}:{idx}" for idx, (source_id, _) in enumerate(entries, start=1)]
        documents = [text for _, text in entries]
        metadatas = [{"source_id": source_id} for source_id, _ in entries]

        # Replace current collection content to keep the dataset deterministic.
        existing = collection.get(include=[])
        existing_ids = existing.get("ids", [])
        if existing_ids:
            collection.delete(ids=existing_ids)

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        self.stdout.write(self.style.SUCCESS(f"Ingested {len(entries)} RAG snippets from {src_path}"))
