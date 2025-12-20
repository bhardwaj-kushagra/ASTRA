"""Threat exchange helpers for ASTRA (Phase 3).

This implements a lightweight, versioned JSON format for exchanging threat
summaries between two running ASTRA instances over HTTP.

Design goals:
- No Kafka/queues required (MVP is REST pull/push).
- SQLite-friendly queries.
- Schema is explicit and versioned.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


SCHEMA_VERSION = "astra-threat-exchange-1.0"


class ThreatExchangeProducer(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the producing instance")
    service: str = Field(default="risk-analytics")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    base_url: Optional[str] = Field(default=None, description="Optional base URL of the producer")


class ThreatIndicator(BaseModel):
    actor_id: Optional[str] = Field(default=None)
    source_hash: Optional[str] = Field(default=None)
    detection_label: str
    max_confidence: float = Field(..., ge=0.0, le=1.0)
    event_count: int = Field(..., ge=1)
    first_seen: datetime
    last_seen: datetime


class ThreatExchangeEnvelope(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    producer: ThreatExchangeProducer
    indicators: List[ThreatIndicator] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


def build_summary(*, indicators: List[ThreatIndicator]) -> Dict[str, Any]:
    by_label: Dict[str, int] = {}
    for ind in indicators:
        by_label[ind.detection_label] = by_label.get(ind.detection_label, 0) + int(ind.event_count)

    return {
        "indicator_count": len(indicators),
        "events_by_label": by_label,
    }
