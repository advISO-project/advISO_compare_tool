# Copyright (C) 2026 Cardiff University, the Wellcome Sanger Institute and
# the University of the Western Cape
# SPDX-License-Identifier: GPL-3.0-or-later

"""Align validated reference and query records by canonical identity."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from adviso_compare.records import KeyedRecord, RecordKey, RecordModel


class RecordDisposition(str, Enum):
    """Relationship of one canonical key across the two datasets."""

    MATCHED = "matched"
    MISSING = "missing"
    EXTRA = "extra"


@dataclass(frozen=True, slots=True)
class RecordAlignment:
    """Reference and query records sharing one canonical key, where present."""

    key: RecordKey
    reference: KeyedRecord | None
    query: KeyedRecord | None
    disposition: RecordDisposition

    @property
    def canonical_identity(self) -> tuple[str, ...]:
        """Return the canonical textual key components in configured order."""
        record = self.reference if self.reference is not None else self.query
        if record is None:
            raise AssertionError("record alignment has neither side")
        return record.canonical_identity


@dataclass(frozen=True, slots=True)
class RecordCounts:
    """Reconciled record counts for later canonical summary generation."""

    reference: int
    query: int
    matched: int
    missing: int
    extra: int


@dataclass(frozen=True, slots=True)
class RecordsResult:
    """Complete deterministic alignment of two valid record models."""

    alignments: tuple[RecordAlignment, ...]
    counts: RecordCounts
    _alignment_index: Mapping[RecordKey, RecordAlignment]

    def alignment(self, record_key: RecordKey) -> RecordAlignment:
        """Return the alignment for one canonical record key."""
        return self._alignment_index[record_key]

    @property
    def matched(self) -> tuple[RecordAlignment, ...]:
        """Return safely aligned records available to the values phase."""
        return tuple(
            alignment
            for alignment in self.alignments
            if alignment.disposition is RecordDisposition.MATCHED
        )


def align_records(
    reference: RecordModel,
    query: RecordModel,
) -> RecordsResult:
    """Classify the union of two valid record-key indexes."""
    keys = set(reference.by_key) | set(query.by_key)
    ordered_keys = sorted(
        keys,
        key=lambda key: tuple(component.text for component in key),
    )
    alignments: list[RecordAlignment] = []

    for key in ordered_keys:
        reference_record = reference.by_key.get(key)
        query_record = query.by_key.get(key)
        if reference_record is not None and query_record is not None:
            disposition = RecordDisposition.MATCHED
        elif reference_record is not None:
            disposition = RecordDisposition.MISSING
        elif query_record is not None:
            disposition = RecordDisposition.EXTRA
        else:
            raise AssertionError("record-key union contains no record")
        alignment = RecordAlignment(
            key=key,
            reference=reference_record,
            query=query_record,
            disposition=disposition,
        )
        alignments.append(alignment)

    matched = sum(
        alignment.disposition is RecordDisposition.MATCHED for alignment in alignments
    )
    missing = sum(
        alignment.disposition is RecordDisposition.MISSING for alignment in alignments
    )
    extra = sum(
        alignment.disposition is RecordDisposition.EXTRA for alignment in alignments
    )
    alignment_tuple = tuple(alignments)
    return RecordsResult(
        alignments=alignment_tuple,
        counts=RecordCounts(
            reference=len(reference.records),
            query=len(query.records),
            matched=matched,
            missing=missing,
            extra=extra,
        ),
        _alignment_index=MappingProxyType(
            {alignment.key: alignment for alignment in alignment_tuple}
        ),
    )
