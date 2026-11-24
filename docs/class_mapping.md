# Class Mapping

Owners: Model Team + Dashboard Team. Decisions D-005, D-006, D-007.

## Training / paper reproduction: 6 classes

IDs are fixed and match the CHV README and Table 2 of the paper. **Never reorder them.**

| ID | Name (exact string) |
|---|---|
| 0 | `person` |
| 1 | `vest` |
| 2 | `blue_helmet` |
| 3 | `red_helmet` |
| 4 | `white_helmet` |
| 5 | `yellow_helmet` |

## Live system: 3 classes

The model is trained with 6 classes; the live pipeline merges the helmet colours after detection.

| Training ID(s) | Live name (exact string) |
|---|---|
| 0 | `person` |
| 1 | `vest` |
| 2, 3, 4, 5 | `helmet` |

```python
LIVE_CLASS = {0: "person", 1: "vest", 2: "helmet", 3: "helmet", 4: "helmet", 5: "helmet"}
```

## Violation statuses (derived, not detected)

There is no "missing PPE" class. For each tracked person:
- A **helmet** belongs to the person if its centre is inside the top part of the person's box.
- A **vest** belongs to the person if its centre is inside the middle part of the person's box.
- The exact thresholds are tuned by the Model Team and recorded here once fixed.

| Status (exact string) | Meaning |
|---|---|
| `compliant` | helmet and vest found |
| `no_helmet` | vest found, no helmet |
| `no_vest` | helmet found, no vest |
| `no_helmet_no_vest` | neither found |

## Out of scope for v1

Gloves, safety shoes, masks, glasses: not annotated, not detected.

## Annotation notes for the Egyptian images

To be expanded into the one-page annotation guide before labelling starts:
- Use the 6 IDs above, YOLO format (`class x_center y_center width height`, normalised).
- Label every visible person, even if partly visible. *(to confirm)*
- Helmets carried, not worn: label as a helmet of its colour. *(to confirm)*
- Faded colours: pick the closest of the 4 colours. *(to confirm)*
- **Orange helmets → `red_helmet` (ID 3).** Decided (D-016).
- Heads with no helmet (bare head, cap, cloth wrap) get **no** helmet box.
- Yellow/orange objects that are not helmets (tools, gloves, paint marks on walls) get no box.
