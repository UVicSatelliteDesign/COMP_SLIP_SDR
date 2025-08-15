import numpy as np
import matplotlib.pyplot as plt

# Path to your .cfile
CFILENAME = "./scripts/tx_baseband.cfile"

# Load complex64 samples (float32 real + float32 imag)
print(f"[INFO] Reading {CFILENAME} ...")
data = np.fromfile(CFILENAME, dtype=np.complex64)

# Show first few samples
print(f"[INFO] Loaded {len(data)} complex samples")
print("First 10 samples:")
print(data[:10])

# Plot constellation
plt.figure(figsize=(6, 6))
plt.scatter(data.real, data.imag, s=1, alpha=0.5)
plt.title("Constellation from tx_baseband.cfile")
plt.xlabel("In-phase (I)")
plt.ylabel("Quadrature (Q)")
plt.grid(True)
plt.axis('equal')
plt.show()
