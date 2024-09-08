import pyautogui
import time
from PIL import Image, ImageOps
import tkinter as tk
import threading
import keyboard  # To detect global keypresses

# Constants
MAX_WIDTH, MAX_HEIGHT = 250, 110
PIXEL_BLOCK_SIZE = 4  # Size of each blocky pixel in the final drawing
CLICK_DURATION = 0.5  # Duration of the click and drag

# Flag to track whether the drawing should stop
stop_drawing = False

def start_drawing_thread(image_path):
    global stop_drawing
    stop_drawing = False

    def process_and_draw_image():
        try:
            # Open the image using Pillow
            img = Image.open(image_path)

            # Convert image to grayscale (black and white)
            img = ImageOps.grayscale(img)

            # Resize the image to fit within 250x110 while maintaining aspect ratio
            img.thumbnail((MAX_WIDTH // PIXEL_BLOCK_SIZE, MAX_HEIGHT // PIXEL_BLOCK_SIZE))

            # Convert image to strictly black (0) and white (255) based on a threshold
            threshold = 128  # You can adjust the threshold for black and white conversion
            img = img.point(lambda p: p > threshold and 255)

            # Interpolate and expand the image back to a blocky version
            img = img.resize((img.width * PIXEL_BLOCK_SIZE, img.height * PIXEL_BLOCK_SIZE), Image.NEAREST)

            # Get pixel data from the interpolated image
            pixels = img.load()

            # Get image dimensions after resizing
            width, height = img.size

            # Get the current mouse position (starting point for drawing)
            start_x, start_y = pyautogui.position()

            # Add a delay to give the user time to move the mouse to the drawing area
            print("Starting in 3 seconds... Move the mouse to the starting point.")
            time.sleep(3)

            # Iterate over each pixel block in the image
            for y in range(0, height, PIXEL_BLOCK_SIZE):
                for x in range(0, width, PIXEL_BLOCK_SIZE):
                    # Check for stop condition
                    if stop_drawing:
                        print("Drawing stopped by user.")
                        return

                    # If the pixel is black, press and drag the mouse
                    if pixels[x, y] == 0:  # Black pixel
                        # Move to the starting point of the block
                        pyautogui.moveTo(start_x + x, start_y + y)

                        # Simulate mouse press and drag
                        pyautogui.mouseDown()  # Press the mouse button
                        time.sleep(CLICK_DURATION)  # Hold for half a second

                        # Slight drag within the block to simulate a drawn line
                        pyautogui.moveTo(start_x + x + PIXEL_BLOCK_SIZE, start_y + y + PIXEL_BLOCK_SIZE)
                        pyautogui.mouseUp()  # Release the mouse button after dragging

            print("Drawing complete!")

        except Exception as e:
            print(f"Error: {e}")

    # Start the drawing process in a separate thread
    drawing_thread = threading.Thread(target=process_and_draw_image)
    drawing_thread.start()

def stop_drawing_key():
    global stop_drawing
    # Continuously listen for the "f" key press globally
    while True:
        if keyboard.is_pressed('f'):
            stop_drawing = True
            print("Stopping drawing due to 'f' key press.")
            break

# Main script execution
if __name__ == "__main__":
    # Provide a static file path for testing (replace with your own image file)
    image_path = 'in.png'  # Replace this with the path to your image

    # Create a small tkinter window to provide user instructions
    root = tk.Tk()
    root.geometry("300x100")
    root.title("Press 'f' to stop drawing")

    # Display instructions in the tkinter window
    label = tk.Label(root, text="Close window and press 'f' key to stop drawing.")
    label.pack(pady=20)

    # Start the drawing process in a separate thread
    start_drawing_thread(image_path)

    # Start the key listener in a separate thread
    key_listener_thread = threading.Thread(target=stop_drawing_key)
    key_listener_thread.start()

    # Start the tkinter main loop (can close this window while drawing continues)
    root.mainloop()

    # Wait for the key listener thread to finish
    key_listener_thread.join()
