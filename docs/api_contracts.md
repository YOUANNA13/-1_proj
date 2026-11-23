# API Contracts: Live Pipeline ↔ Backend ↔ Dashboard

Owner: Dashboard Team (owns the contract) + Model Team. Decision D-012.
**Status: draft. The Dashboard Team must confirm it before anyone builds on it.**

## Flow

```
Camera → Live pipeline (Model Team) ──POST /api/ingest/events──▶ Backend (Dashboard Team)
                                                                   │ stores in DB
                                                                   └──WebSocket /ws/alerts──▶ Dashboard
```

## Shared rules

- Time: ISO-8601 in UTC, e.g. `2026-11-23T10:15:02Z`.
- Boxes: pixel coordinates `[x1, y1, x2, y2]` on the original frame.
- Class and status names: exactly as in `docs/class_mapping.md`.
- IDs: `event_id` and `alert_id` are UUID strings.

## Database tables

### `cameras`
| Column | Type | Notes |
|---|---|---|
| id | TEXT PK | e.g. `cam1` |
| name | TEXT | |
| location | TEXT | |
| stream_url | TEXT | USB index or RTSP URL |
| active | BOOLEAN | |

### `tracks` (one tracked person)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| camera_id | TEXT FK → cameras | |
| track_id | INTEGER | ByteTrack ID, unique per camera session |
| first_seen | TIMESTAMP | |
| last_seen | TIMESTAMP | |

### `events` (one violation)
| Column | Type | Notes |
|---|---|---|
| id | TEXT PK | `event_id` |
| camera_id | TEXT FK → cameras | |
| track_id | INTEGER | |
| violation | TEXT | `no_helmet` / `no_vest` / `no_helmet_no_vest` |
| start_ts | TIMESTAMP | |
| end_ts | TIMESTAMP NULL | NULL while ongoing |
| confidence | REAL | |
| bbox | TEXT (JSON) | person box at alert time |
| snapshot_path | TEXT | saved frame |

### `alerts`
| Column | Type | Notes |
|---|---|---|
| id | TEXT PK | `alert_id` |
| event_id | TEXT FK → events | |
| sent_ts | TIMESTAMP | |
| acknowledged | BOOLEAN | |
| ack_ts | TIMESTAMP NULL | |

### `daily_stats`
| Column | Type | Notes |
|---|---|---|
| date | DATE | |
| camera_id | TEXT | |
| persons_seen | INTEGER | |
| helmet_compliance | REAL | 0–1 |
| vest_compliance | REAL | 0–1 |
| safety_index | REAL | 0.75 × helmet + 0.25 × vest |
| violations | INTEGER | |

## Pipeline → Backend

### `POST /api/ingest/events`
Sent by the live pipeline when a violation starts, and again when it ends.
```json
{
  "event_id": "8f1c…",
  "camera_id": "cam1",
  "track_id": 17,
  "violation": "no_helmet",
  "state": "start",
  "ts": "2026-11-23T10:15:02Z",
  "confidence": 0.87,
  "bbox": [412, 120, 530, 460],
  "snapshot_jpeg_base64": "…"
}
```
`state` is `start` or `end`. Response: `201 {"event_id": "…", "alert_id": "…"}`.

## Backend → Dashboard (WebSocket `/ws/alerts`)

```json
{
  "type": "violation",
  "alert_id": "c2d9…",
  "event_id": "8f1c…",
  "camera_id": "cam1",
  "track_id": 17,
  "violation": "no_helmet",
  "ts": "2026-11-23T10:15:02Z",
  "bbox": [412, 120, 530, 460],
  "snapshot_url": "/api/snapshots/8f1c….jpg"
}
```
Other message types: `{"type": "event_end", "event_id": "…", "ts": "…"}` and `{"type": "stats", ...}` (live counters).

## REST endpoints (Dashboard → Backend)

| Method | Path | Returns |
|---|---|---|
| GET | `/api/events?from=&to=&camera=&violation=` | list of events |
| GET | `/api/alerts?acknowledged=` | list of alerts |
| POST | `/api/alerts/{alert_id}/ack` | acknowledged alert |
| GET | `/api/statistics?from=&to=&camera=` | compliance %, Safety Index, counts per violation |
| GET | `/api/cameras` | list of cameras |
| GET | `/api/snapshots/{file}` | snapshot image |
