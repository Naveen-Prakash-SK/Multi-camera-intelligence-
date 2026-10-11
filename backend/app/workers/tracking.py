def compute_iou(boxA, boxB):
    xA = max(boxA['x1'], boxB['x1'])
    yA = max(boxA['y1'], boxB['y1'])
    xB = min(boxA['x2'], boxB['x2'])
    yB = min(boxA['y2'], boxB['y2'])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA['x2'] - boxA['x1']) * (boxA['y2'] - boxA['y1'])
    boxBArea = (boxB['x2'] - boxB['x1']) * (boxB['y2'] - boxB['y1'])
    iou = interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0
    return iou

class Tracker:
    def __init__(self):
        self.tracks = {} # track_id -> dict of last seen box, etc.
        self.next_id = 1

    def update(self, detections, camera_id, timestamp_s):
        """
        detections: list of dicts with 'bbox', 'label', 'confidence', 'attributes'
        Returns detections with 'track_id' added.
        """
        updated_detections = []
        for det in detections:
            best_iou = 0.3 # threshold
            best_track = None
            for tid, tinfo in self.tracks.items():
                if tinfo['label'] != det['label']: continue
                iou = compute_iou(det['bbox'], tinfo['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_track = tid
            
            if best_track is not None:
                track_id = best_track
            else:
                track_id = f"track_{camera_id}_{self.next_id}"
                self.next_id += 1
                
            self.tracks[track_id] = {
                'bbox': det['bbox'],
                'label': det['label'],
                'last_seen': timestamp_s
            }
            
            det_out = det.copy()
            det_out['track_id'] = track_id
            updated_detections.append(det_out)
            
        # Cleanup old tracks (e.g., unseen for > 2 seconds)
        to_delete = [tid for tid, tinfo in self.tracks.items() if timestamp_s - tinfo['last_seen'] > 2.0]
        for tid in to_delete:
            del self.tracks[tid]
            
        return updated_detections
