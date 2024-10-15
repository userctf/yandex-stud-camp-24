import cv2

# Open a video capture object (0 for the default camera, or provide a video file path)
cap = cv2.VideoCapture("http://192.168.2.106:8080/?action=stream")

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()
    
    # Check if the frame was captured successfully
    if not ret:
        break
    
    # Get the dimensions of the frame
    height, width, _ = frame.shape
    
    # Calculate the center x-coordinate
    center_x = width // 2
    
    # Draw a vertical line at the center of the frame
    cv2.line(frame, (center_x, 0), (center_x, height), (0, 255, 0), 2)  # Green line with thickness 2
    
    # Display the frame with the vertical line
    cv2.imshow('Video Stream with Vertical Line', frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()