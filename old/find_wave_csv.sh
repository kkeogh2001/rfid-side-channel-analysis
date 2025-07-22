USER_GVFS=/run/user/$(id -u)/gvfs
MTP_LABEL=$(ls "$USER_GVFS" | grep mtp:host)
MTP_ROOT="$USER_GVFS/$MTP_LABEL"
echo "Mounted at: $MTP_ROOT"
ls "$MTP_ROOT/USB Front"
cp "$MTP_ROOT/USB Front/"*.CSV ~/Desktop/
echo "✅ Copied $(basename "$MTP_ROOT/USB Front/"*.CSV) to ~/Desktop"
head -n 20 ~/Desktop/$(basename "$MTP_ROOT/USB Front/"*.CSV)
