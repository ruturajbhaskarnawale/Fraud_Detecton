try:
    import mediapipe as mp
    print(f"MediaPipe version: {mp.__version__}")
    from mediapipe.python.solutions import face_mesh
    print("Imported face_mesh from mediapipe.python.solutions")
except Exception as e:
    print(f"Error: {e}")
