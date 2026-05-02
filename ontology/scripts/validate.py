"""Console entrypoint shim for ontology validation."""

from .validate_ontology import main


if __name__ == "__main__":
    raise SystemExit(main())
