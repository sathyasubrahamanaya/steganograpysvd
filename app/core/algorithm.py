import numpy as np
import pywt
import cv2

# --- Embedding (Optimized) ---
def embed(cover_path, message_path, scale_factor=0.05):  # Adjusted scaling
    # Read images
    cover = cv2.imread(cover_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
    message = cv2.imread(message_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)

    # Apply DWT to cover (level=1 for simplicity)
    coeffs = pywt.wavedec2(cover, 'haar', level=1)
    LL, (LH, HL, HH) = coeffs

    # Ensure message fits into HH component
    max_hidden_size = HH.size
    if message.size > max_hidden_size:
        new_size = int(np.sqrt(max_hidden_size))
        message = cv2.resize(message, (new_size, new_size))

    # Apply SVD to message
    U, S, Vt = np.linalg.svd(message, full_matrices=False)

    # Normalize S to [0, 1] and scale
    S_normalized = (S - S.min()) / (S.max() - S.min())  # Normalization
    S_scaled = S_normalized * 255 * scale_factor  # Dynamic scaling

    # Embed into HH component
    HH_flat = HH.flatten()
    HH_flat[:len(S_scaled)] = S_scaled
    HH_embedded = HH_flat.reshape(HH.shape)

    # Reconstruct stego image
    coeffs_embedded = (LL, (LH, HL, HH_embedded))
    stego = pywt.waverec2(coeffs_embedded, 'haar')
    stego_uint8 = np.clip(stego, 0, 255).astype(np.uint8)

    return stego_uint8, U, Vt, scale_factor, S # Return S as well


# --- Extraction (Optimized) ---
def extract(stego_uint8, U, Vt, scale_factor, S): # Pass S as an argument
    # Convert to float32 for precision
    stego = stego_uint8.astype(np.float32)

    # Apply DWT
    coeffs = pywt.wavedec2(stego, 'haar', level=1)
    LL, (LH, HL, HH_embedded) = coeffs

    # Extract and denormalize S
    HH_flat = HH_embedded.flatten()
    len_S = min(U.shape[0], Vt.shape[1])
    S_extracted = HH_flat[:len_S]

    # Reverse scaling and normalization
    S_denormalized = (S_extracted / (255 * scale_factor)) * (S.max() - S.min()) + S.min()

    # Reconstruct message
    message_reconstructed = U @ np.diag(S_denormalized) @ Vt
    message_reconstructed = np.clip(message_reconstructed, 0, 255).astype(np.uint8)

    # Gentle contrast enhancement
    message_reconstructed = cv2.normalize(
        message_reconstructed, None, 0, 255, cv2.NORM_MINMAX
    )

    return message_reconstructed