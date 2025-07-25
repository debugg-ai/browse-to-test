#!/bin/bash

# Browse-to-Test Sample App Test Runner
# This script runs the verification tests with different configurations

echo "🚀 Browse-to-Test Sample App Test Runner"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  No virtual environment detected. Consider using one."
fi

# Check if browse-to-test is installed
if python -c "import browse_to_test" 2>/dev/null; then
    echo "✅ browse-to-test library is installed"
else
    echo "❌ browse-to-test library not found!"
    echo "📦 Installing browse-to-test[all]..."
    pip install browse-to-test[all]
fi

# Check for API keys
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "⚠️  OPENAI_API_KEY not set. Some tests may fail."
fi

if [[ -z "$ANTHROPIC_API_KEY" ]]; then
    echo "⚠️  ANTHROPIC_API_KEY not set. Anthropic tests will be skipped."
fi

echo ""
echo "🧪 Running test scenarios..."
echo ""

# Test 1: Simple demo
echo "1️⃣ Running simple demo..."
python simple_demo.py
echo ""

# Test 2: Full verification with OpenAI
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "2️⃣ Running full verification with OpenAI..."
    python main.py --ai-provider openai
    echo ""
else
    echo "2️⃣ Skipping OpenAI tests (no API key)"
    echo ""
fi

# Test 3: Full verification with Anthropic (if available)
if [[ -n "$ANTHROPIC_API_KEY" ]]; then
    echo "3️⃣ Running full verification with Anthropic..."
    python main.py --ai-provider anthropic
    echo ""
else
    echo "3️⃣ Skipping Anthropic tests (no API key)"
    echo ""
fi

# Test 4: Verbose mode (if OpenAI available)
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "4️⃣ Running verbose verification..."
    python main.py --ai-provider openai --verbose
    echo ""
fi

echo "🎉 All test scenarios completed!"
echo ""
echo "📁 Generated files in output/:"
ls -la output/ 2>/dev/null || echo "   No output directory found"

echo ""
echo "📋 To run individual tests:"
echo "   python simple_demo.py"
echo "   python main.py --help"
echo "   python main.py --ai-provider openai --verbose" 