"""Matching utilities for tracking."""


def compute_iou(bbox1: tuple[float, float, float, float],
                bbox2: tuple[float, float, float, float]) -> float:
    """
    Compute Intersection over Union (IoU) for two bounding boxes.
    
    Args:
        bbox1, bbox2: Bounding boxes as (x, y, w, h) in normalized coordinates
    
    Returns:
        IoU score between 0 and 1
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    
    # Convert to (x1, y1, x2, y2) format
    box1_x1, box1_y1 = x1, y1
    box1_x2, box1_y2 = x1 + w1, y1 + h1
    
    box2_x1, box2_y1 = x2, y2
    box2_x2, box2_y2 = x2 + w2, y2 + h2
    
    # Compute intersection
    inter_x1 = max(box1_x1, box2_x1)
    inter_y1 = max(box1_y1, box2_y1)
    inter_x2 = min(box1_x2, box2_x2)
    inter_y2 = min(box1_y2, box2_y2)
    
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0
    
    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    
    # Compute union
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area


def match_detections_to_tracks(
    detections: list[tuple[int, tuple[float, float, float, float]]],
    tracks: dict[int, tuple[float, float, float, float]],
    iou_threshold: float = 0.3,
) -> tuple[dict[int, int], list[int], list[int]]:
    """
    Match detections to existing tracks using IoU.
    
    Args:
        detections: List of (detection_idx, bbox) tuples
        tracks: Dict of {track_id: bbox}
        iou_threshold: Minimum IoU for a match
    
    Returns:
        (matches, unmatched_detections, unmatched_tracks)
        - matches: {detection_idx: track_id}
        - unmatched_detections: List of detection indices
        - unmatched_tracks: List of track IDs
    """
    if not detections or not tracks:
        unmatched_det = [d[0] for d in detections]
        unmatched_trk = list(tracks.keys())
        return {}, unmatched_det, unmatched_trk
    
    # Compute IoU matrix
    iou_matrix = {}
    for det_idx, det_bbox in detections:
        for track_id, track_bbox in tracks.items():
            iou = compute_iou(det_bbox, track_bbox)
            if iou >= iou_threshold:
                iou_matrix[(det_idx, track_id)] = iou
    
    # Greedy matching (highest IoU first)
    matches = {}
    matched_detections = set()
    matched_tracks = set()
    
    # Sort by IoU descending
    sorted_pairs = sorted(iou_matrix.items(), key=lambda x: x[1], reverse=True)
    
    for (det_idx, track_id), iou in sorted_pairs:
        if det_idx not in matched_detections and track_id not in matched_tracks:
            matches[det_idx] = track_id
            matched_detections.add(det_idx)
            matched_tracks.add(track_id)
    
    # Identify unmatched
    all_det_indices = {d[0] for d in detections}
    all_track_ids = set(tracks.keys())
    
    unmatched_detections = list(all_det_indices - matched_detections)
    unmatched_tracks = list(all_track_ids - matched_tracks)
    
    return matches, unmatched_detections, unmatched_tracks

