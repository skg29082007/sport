"""
Invisible Watermarking Engine for SportShield AI.
Uses DCT-domain embedding to create imperceptible but detectable watermarks.
"""

import cv2
import numpy as np
from PIL import Image
import os


class WatermarkEngine:
    """DCT-domain invisible watermarking for media authentication."""

    BLOCK_SIZE = 8
    ALPHA = 10  # Watermark strength — higher = more robust but more visible

    @classmethod
    def embed_watermark(cls, image_path: str, watermark_id: str, output_path: str) -> bool:
        """
        Embed an invisible watermark into an image using DCT coefficients.
        
        Args:
            image_path: Path to the original image
            watermark_id: Unique ID string to embed
            output_path: Path to save the watermarked image
            
        Returns:
            True if successful
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False

            # Convert to YCrCb color space — embed in Y (luminance) channel
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            y_channel = ycrcb[:, :, 0].astype(np.float64)

            # Convert watermark_id to binary bits
            wm_bits = cls._string_to_bits(watermark_id)

            # Get dimensions for block processing
            h, w = y_channel.shape
            bh = (h // cls.BLOCK_SIZE) * cls.BLOCK_SIZE
            bw = (w // cls.BLOCK_SIZE) * cls.BLOCK_SIZE

            # Embed watermark bits into DCT mid-frequency coefficients
            bit_idx = 0
            for i in range(0, bh, cls.BLOCK_SIZE):
                for j in range(0, bw, cls.BLOCK_SIZE):
                    if bit_idx >= len(wm_bits):
                        break

                    block = y_channel[i : i + cls.BLOCK_SIZE, j : j + cls.BLOCK_SIZE]
                    dct_block = cv2.dct(block)

                    # Embed in mid-frequency coefficient (4,3)
                    bit = wm_bits[bit_idx]
                    if bit == 1:
                        dct_block[4, 3] = abs(dct_block[4, 3]) + cls.ALPHA
                    else:
                        dct_block[4, 3] = -abs(dct_block[4, 3]) - cls.ALPHA

                    # Inverse DCT
                    y_channel[i : i + cls.BLOCK_SIZE, j : j + cls.BLOCK_SIZE] = (
                        cv2.idct(dct_block)
                    )
                    bit_idx += 1

                if bit_idx >= len(wm_bits):
                    break

            # Reconstruct the image
            ycrcb[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
            watermarked = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, watermarked, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return True

        except Exception as e:
            print(f"Watermark embedding error: {e}")
            return False

    @classmethod
    def extract_watermark(cls, image_path: str, expected_length: int = 128) -> str:
        """
        Extract watermark bits from an image.
        
        Args:
            image_path: Path to the potentially watermarked image
            expected_length: Expected number of bits in the watermark
            
        Returns:
            Extracted watermark string, or empty string if not found
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return ""

            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            y_channel = ycrcb[:, :, 0].astype(np.float64)

            h, w = y_channel.shape
            bh = (h // cls.BLOCK_SIZE) * cls.BLOCK_SIZE
            bw = (w // cls.BLOCK_SIZE) * cls.BLOCK_SIZE

            extracted_bits = []
            for i in range(0, bh, cls.BLOCK_SIZE):
                for j in range(0, bw, cls.BLOCK_SIZE):
                    if len(extracted_bits) >= expected_length:
                        break

                    block = y_channel[i : i + cls.BLOCK_SIZE, j : j + cls.BLOCK_SIZE]
                    dct_block = cv2.dct(block)

                    # Read bit from mid-frequency coefficient
                    if dct_block[4, 3] > 0:
                        extracted_bits.append(1)
                    else:
                        extracted_bits.append(0)

                if len(extracted_bits) >= expected_length:
                    break

            return cls._bits_to_string(extracted_bits)

        except Exception as e:
            print(f"Watermark extraction error: {e}")
            return ""

    @classmethod
    def verify_watermark(cls, image_path: str, expected_id: str) -> dict:
        """
        Verify if an image contains the expected watermark.
        
        Returns:
            dict with 'found', 'extracted_id', and 'confidence'
        """
        expected_bits = cls._string_to_bits(expected_id)
        extracted = cls.extract_watermark(image_path, len(expected_bits))
        extracted_bits = cls._string_to_bits(extracted) if extracted else []

        if not extracted_bits or not expected_bits:
            return {"found": False, "extracted_id": "", "confidence": 0.0}

        # Calculate bit agreement
        min_len = min(len(expected_bits), len(extracted_bits))
        if min_len == 0:
            return {"found": False, "extracted_id": extracted, "confidence": 0.0}

        matches = sum(
            1 for a, b in zip(expected_bits[:min_len], extracted_bits[:min_len])
            if a == b
        )
        confidence = matches / min_len

        return {
            "found": confidence > 0.7,
            "extracted_id": extracted,
            "confidence": confidence,
        }

    @staticmethod
    def _string_to_bits(s: str) -> list:
        """Convert a string to a list of bits."""
        bits = []
        for char in s:
            char_bits = format(ord(char), "08b")
            bits.extend([int(b) for b in char_bits])
        return bits

    @staticmethod
    def _bits_to_string(bits: list) -> str:
        """Convert a list of bits back to a string."""
        chars = []
        for i in range(0, len(bits) - 7, 8):
            byte = bits[i : i + 8]
            char_val = int("".join(str(b) for b in byte), 2)
            if 32 <= char_val <= 126:  # Printable ASCII
                chars.append(chr(char_val))
        return "".join(chars)
