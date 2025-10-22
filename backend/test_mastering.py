#!/usr/bin/env python3
import subprocess
import sys

print("🧪 Testing Mastering System\n")

# Create quiet test file
test_input = '/tmp/test_quiet.mp3'
test_output = '/tmp/test_mastered.mp3'

print("1️⃣ Creating quiet test audio...")
subprocess.run([
    'ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=5',
    '-af', 'volume=0.1',
    '-ar', '44100', '-b:a', '192k',
    test_input
], capture_output=True, timeout=10)
print("   ✅ Created\n")

print("2️⃣ Running mastering...")
from powerful_mastering import master_audio_powerful

success = master_audio_powerful(test_input, test_output, target_lufs=-11.0)

if not success:
    print("   ❌ MASTERING FAILED!\n")
    sys.exit(1)

print("   ✅ Completed\n")

print("3️⃣ Comparing loudness...\n")

# Check input
result = subprocess.run([
    'ffmpeg', '-i', test_input, '-af', 'volumedetect', '-f', 'null', '-'
], capture_output=True, text=True, timeout=10)

print("📊 INPUT:")
for line in result.stderr.split('\n'):
    if 'mean_volume' in line or 'max_volume' in line:
        print(f"   {line.strip()}")

# Check output  
result2 = subprocess.run([
    'ffmpeg', '-i', test_output, '-af', 'volumedetect', '-f', 'null', '-'
], capture_output=True, text=True, timeout=10)

print("\n📊 OUTPUT (should be LOUDER):")
for line in result2.stderr.split('\n'):
    if 'mean_volume' in line or 'max_volume' in line:
        print(f"   {line.strip()}")

print("\n✅ Test complete!")
