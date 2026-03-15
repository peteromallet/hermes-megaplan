# VHS tape file for recording Hermes Agent demos
# Install VHS: brew install charmbracelet/tap/vhs
# Record:      vhs demo/record.tape

# Terminal settings
Output demo/output.gif
# Output demo/output.mp4   # Uncomment for MP4
# Output demo/output.webm  # Uncomment for WebM

Set FontSize 14
Set Width 1200
Set Height 800
Set FontFamily "JetBrains Mono"
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 0ms
Set PlaybackSpeed 1

# Run the demo player
Type "python demo/player.py demo/scripts/example.yaml"
Enter
Sleep 45s
