from video_processor import VideoProcessor


# --------------------------------------------------
# Input and output video
# --------------------------------------------------

input_video = "test_videos/3.mp4"

output_video = "computer_vision/output/processed_3.mp4"


# --------------------------------------------------
# Create video processor
# --------------------------------------------------

processor = VideoProcessor(
    input_path=input_video,
    output_path=output_video,
    red_line_y=200,
    blue_line_y=300
)


# --------------------------------------------------
# Process video
# --------------------------------------------------

down_counts, up_counts = processor.process()


# --------------------------------------------------
# Print final results
# --------------------------------------------------

print("\n===================================")
print("       FINAL VEHICLE COUNTS")
print("===================================")

print("\nDOWN COUNTS:")

for vehicle, count in down_counts.items():
    print(f"{vehicle}: {count}")


print("\nUP COUNTS:")

for vehicle, count in up_counts.items():
    print(f"{vehicle}: {count}")


print("\n===================================")
print("Processing completed successfully!")
print("===================================")