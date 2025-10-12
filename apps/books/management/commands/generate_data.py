import random
import string
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.books.models import Book, BookAuthor


def rand_str(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


class Command(BaseCommand):
    help = (
        "Create a given number of authors and a given number of books per author. "
        "Example: manage.py seed_books --author-count 10 --book-count-per-author 5"
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument("--author-count", type=int, required=True)
        parser.add_argument("--book-count-per-author", type=int, required=True)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually writing to the database.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        author_count = options["author_count"]
        per_author = options["book_count_per_author"]
        dry_run = options["dry_run"]

        if author_count <= 0 or per_author < 0:
            raise CommandError(
                "author-count must be > 0 and book-count-per-author must be non-negative."
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would create {author_count} authors and {author_count * per_author} books."
                )
            )
            return

        self.stdout.write(f"Creating {author_count} authors...")
        created_authors: list[BookAuthor] = []

        with transaction.atomic():
            for _ in range(author_count):
                created_authors.append(
                    BookAuthor.objects.create(
                        name=rand_str(8),
                        surname=rand_str(10),
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(created_authors)} authors.")
        )

        total_books = 0
        self.stdout.write(f"Creating {per_author} books per author...")

        with transaction.atomic():
            for author in created_authors:
                books = [
                    Book(title=rand_str(12), author=author) for _ in range(per_author)
                ]
                Book.objects.bulk_create(books)
                total_books += len(books)

        self.stdout.write(self.style.SUCCESS(f"Created {total_books} books total."))
        self.stdout.write(self.style.SUCCESS("Done."))
