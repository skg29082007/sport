"""
Digital Fingerprinting Engine for SportShield AI.
Uses perceptual hashing (pHash, aHash, dHash) to create robust media fingerprints.
"""

import numpy as np
from PIL import Image
import imagehash
import io
import hashlib


class FingerprintEngine:
    """Generate perceptual hashes for media assets."""

    HASH_SIZE = 16  # 16x16 = 256-bit hashes for better precision

    @staticmethod
    def compute_phash(image: Image.Image) -> imagehash.ImageHash:
        """Compute perceptual hash using DCT."""
        return imagehash.phash(image, hash_size=FingerprintEngine.HASH_SIZE)

    @staticmethod
    def compute_ahash(image: Image.Image) -> imagehash.ImageHash:
        """Compute average hash."""
        return imagehash.average_hash(image, hash_size=FingerprintEngine.HASH_SIZE)

    @staticmethod
    def compute_dhash(image: Image.Image) -> imagehash.ImageHash:
        """Compute difference hash."""
        return imagehash.dhash(image, hash_size=FingerprintEngine.HASH_SIZE)

    @classmethod
    def fingerprint(cls, image_path: str) -> dict:
        """
        Generate a complete fingerprint for an image.
        Returns dict with hash strings and numpy vector for FAISS.
        """
        img = Image.open(image_path).convert("RGB")

        phash = cls.compute_phash(img)
        ahash = cls.compute_ahash(img)
        dhash = cls.compute_dhash(img)

        # Convert pHash to a float vector for FAISS indexing
        hash_vector = cls.hash_to_vector(phash)

        return {
            "phash": str(phash),
            "ahash": str(ahash),
            "dhash": str(dhash),
            "vector": hash_vector,
        }

    @classmethod
    def fingerprint_from_bytes(cls, image_bytes: bytes) -> dict:
        """Generate fingerprint from raw image bytes."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        phash = cls.compute_phash(img)
        ahash = cls.compute_ahash(img)
        dhash = cls.compute_dhash(img)

        hash_vector = cls.hash_to_vector(phash)

        return {
            "phash": str(phash),
            "ahash": str(ahash),
            "dhash": str(dhash),
            "vector": hash_vector,
        }

    @staticmethod
    def hash_to_vector(h: imagehash.ImageHash) -> np.ndarray:
        """Convert an ImageHash to a float32 numpy vector for FAISS."""
        return np.array(h.hash.flatten(), dtype=np.float32)

    @staticmethod
    def compute_similarity(hash1: str, hash2: str) -> float:
        """
        Compute similarity between two hash strings.
        Returns a value between 0.0 (identical) and 1.0 (completely different).
        """
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        max_dist = len(h1.hash.flatten())
        distance = h1 - h2
        return 1.0 - (distance / max_dist)

    @staticmethod
    def generate_watermark_id(image_path: str) -> str:
        """Generate a unique watermark ID based on file content."""
        with open(image_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        return f"SS-{content_hash.upper()}"
