import cv2
import numpy as np

class FaceQualityScorer:
    """
    Scores faces based on blur, brightness, and pose.
    Returns a score between 0.0 and 1.0 (1.0 = perfect quality).
    """
    def score(self, face_crop: np.ndarray, landmarks=None) -> float:
        if face_crop is None or face_crop.size == 0:
            return 0.0
            
        # 1. Blur Score (Laplacian variance)
        gray = cv2.cvtColor(face_crop, cv2.COLOR_RGB2GRAY)
        blur_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Typical blur_variance: sharp > 100, blurry < 50
        # Normalize to 0-1 (cap at 200)
        blur_score = min(blur_variance / 200.0, 1.0)
        
        # 2. Brightness Check
        mean_brightness = np.mean(gray)
        # Penalize if too dark (< 30) or too bright (> 225)
        if mean_brightness < 30 or mean_brightness > 225:
            brightness_score = 0.5
        else:
            brightness_score = 1.0
            
        # 3. Pose Score (if landmarks available)
        pose_score = 1.0
        if landmarks is not None and len(landmarks) == 5:
            # Simple heuristic: distance between eyes vs distance from eye to nose
            # Left Eye, Right Eye, Nose, Left Mouth, Right Mouth
            left_eye, right_eye, nose = landmarks[0], landmarks[1], landmarks[2]
            
            # Midpoint of eyes
            eye_mid = (left_eye + right_eye) / 2
            
            # Vector from eye mid to nose
            mid_to_nose = np.linalg.norm(eye_mid - nose)
            eye_dist = np.linalg.norm(left_eye - right_eye)
            
            if eye_dist > 0:
                ratio = mid_to_nose / eye_dist
                # Extreme profiles will have weird ratios
                if ratio > 1.5 or ratio < 0.2:
                    pose_score = 0.5
                    
        # Combine scores (weighted average)
        # Blur is most important for recognition
        final_score = (blur_score * 0.6) + (brightness_score * 0.2) + (pose_score * 0.2)
        
        return float(final_score)
