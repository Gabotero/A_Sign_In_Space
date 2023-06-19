
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image  # Import the Image class from PIL module
from scipy.fftpack import idct

def compute_autocorrelation(bit_stream):
    # Convert the bit stream to a sequence of 1s and -1s
    sequence = np.array(bit_stream) * 2 - 1

    # Compute the autocorrelation using numpy.correlate
    autocorrelation = np.correlate(sequence, sequence, mode='full')

    return autocorrelation

def convert_bits_to_image(image_bits, rows, cols):
    # Reshape the array to match the specified dimensions
    image_array = image_bits.reshape((rows, cols))

    # Convert the array of bits to an array of 0s and 255s
    image_array = np.where(image_array == 0, 0, 255).astype(np.uint8)

    # Create an image from the array
    image = Image.fromarray(image_array)

    return image

def find_max_autocorrelation(autocorrelation):
    max_value = np.max(autocorrelation)
    max_index = np.argmax(autocorrelation)

    return max_value, max_index


# Example usage:
file = open("raw_data.bin", "rb")
image_bytes = file.read()
file.close()

print("Number of bits in the image: ", len(image_bytes)*8, ".")

print("Header bytes: ")
for b in image_bytes[:20]:
	print(int(b), "" , end='')

print("")

print("Trailer bytes: ")
for b in image_bytes[-20:]:
        print(int(b), "" , end='')

print("")


# Remove the first 10 and last 10 bytes
image_bytes = image_bytes[10:-10]

# Convert the bytes to a numpy array of bits
image_bits = np.unpackbits(np.frombuffer(image_bytes, dtype=np.uint8))

autocorrelation = compute_autocorrelation(image_bits)

max_value, max_index = find_max_autocorrelation(autocorrelation)
print("Maximum Autocorrelation:", max_value)
print("Index of Maximum Autocorrelation:", max_index)

plt.plot(autocorrelation[1:1000], marker='o')
plt.xlabel('Offset')
plt.ylabel('Autocorrelation')
plt.title('Autocorrelation Plot')
plt.grid(True)
plt.show()


# Convert the specific arrangement of the bit stream to an image
image = convert_bits_to_image(image_bits, 256, 256)
image.show()
