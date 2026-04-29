#!/bin/bash
# Build a plugin or a single skill.
#
# Usage:
#   ./build.sh <plugin-name>                  — build the full plugin
#   ./build.sh <plugin-name> <skill-name>     — build a single skill
#
# Examples:
#   ./build.sh brief-agent
#   ./build.sh brief-agent brief-business
#   ./build.sh brief-agent brief-assets-builder
#   ./build.sh brief-agent brief-implementation-documents
#
# Plugin directories are expected at the root of this folder (e.g. ./brief-agent/).
# Skill directories are expected at <plugin-name>/skills/<skill-name>/.
# Output: <plugin-name>/build/<name>.zip

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_NAME="$1"
SKILL_NAME="$2"

if [ -z "$PLUGIN_NAME" ]; then
  echo "Usage:"
  echo "  ./build.sh <plugin-name>                 — build the full plugin"
  echo "  ./build.sh <plugin-name> <skill-name>    — build a single skill"
  echo ""
  echo "Available plugins: $(ls -d "$SCRIPT_DIR"/*/  2>/dev/null | xargs -I{} basename {} | tr '\n' ' ')"
  exit 1
fi

PLUGIN_DIR="$SCRIPT_DIR/$PLUGIN_NAME"
BUILD_DIR="$PLUGIN_DIR/build"

if [ ! -d "$PLUGIN_DIR" ]; then
  echo "❌ Plugin '$PLUGIN_NAME' not found at $PLUGIN_DIR"
  exit 1
fi

mkdir -p "$BUILD_DIR"

# ── Build a single skill ──────────────────────────────────────────────────────
if [ -n "$SKILL_NAME" ]; then
  SKILL_DIR="$PLUGIN_DIR/skills/$SKILL_NAME"
  OUTPUT="$BUILD_DIR/$SKILL_NAME.zip"

  if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ Skill '$SKILL_NAME' not found at $SKILL_DIR"
    echo "Available skills: $(ls -d "$PLUGIN_DIR/skills"/*/ 2>/dev/null | xargs -I{} basename {} | tr '\n' ' ')"
    exit 1
  fi

  if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ No SKILL.md found in $SKILL_DIR — is this a valid skill?"
    exit 1
  fi

  echo "📦 Building $SKILL_NAME.zip..."

  rm -f /tmp/"$SKILL_NAME".zip
  cd "$SKILL_DIR" && zip -r /tmp/"$SKILL_NAME".zip . \
    --exclude "*.zip" \
    --exclude "*.skill" \
    --exclude "*.plugin" \
    --exclude "__pycache__/*" \
    --exclude "*.pyc" \
    --exclude ".DS_Store" \
    -q
  cd - > /dev/null
  cp /tmp/"$SKILL_NAME".zip "$OUTPUT"
  cp "$OUTPUT" "$BUILD_DIR/$SKILL_NAME.skill"

  echo "✅ $BUILD_DIR/$SKILL_NAME.zip + .skill built successfully ($(du -sh "$OUTPUT" | cut -f1))."
  exit 0
fi

# ── Build the full plugin ─────────────────────────────────────────────────────
OUTPUT="$BUILD_DIR/$PLUGIN_NAME.zip"

if [ ! -f "$PLUGIN_DIR/.claude-plugin/plugin.json" ]; then
  echo "❌ No .claude-plugin/plugin.json found in $PLUGIN_DIR — is this a valid plugin?"
  exit 1
fi

echo "📦 Building $PLUGIN_NAME.zip..."

rm -f /tmp/"$PLUGIN_NAME".zip
cd "$PLUGIN_DIR" && zip -r /tmp/"$PLUGIN_NAME".zip . \
  --exclude "*.zip" \
  --exclude "*.skill" \
  --exclude "*.plugin" \
  --exclude "__pycache__/*" \
  --exclude "*.pyc" \
  --exclude ".DS_Store" \
  --exclude "*/customers/*" \
  --exclude "build/*" \
  -q
cd - > /dev/null
cp /tmp/"$PLUGIN_NAME".zip "$OUTPUT"
cp "$OUTPUT" "$BUILD_DIR/$PLUGIN_NAME.skill"

echo "✅ $BUILD_DIR/$PLUGIN_NAME.zip + .skill built successfully ($(du -sh "$OUTPUT" | cut -f1))."
