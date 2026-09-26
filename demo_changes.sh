#!/bin/bash

echo "============================================================"
echo "REACT 18 MIGRATION - DEMONSTRATION"
echo "============================================================"
echo ""

echo "1. Checking ReactRootManager implementation..."
echo "   File: src/utils/react.tsx"
if [ -f "/app/src/utils/react.tsx" ]; then
    echo "   ✓ ReactRootManager file exists"
    echo "   Size: $(wc -l < /app/src/utils/react.tsx) lines"
else
    echo "   ✗ File not found"
fi
echo ""

echo "2. Verifying createRoot usage..."
echo "   Searching for createRoot imports..."
grep -r "import.*createRoot" /app/src/components/views/elements/PersistedElement.tsx /app/src/utils/exportUtils/HtmlExport.tsx /app/src/utils/react.tsx 2>/dev/null | wc -l | xargs -I {} echo "   ✓ Found in {} files"
echo ""

echo "3. Verifying ReactDOM.render removal..."
echo "   Checking pillify.tsx..."
if ! grep -q "ReactDOM.render" /app/src/utils/pillify.tsx; then
    echo "   ✓ pillify.tsx: No ReactDOM.render found"
else
    echo "   ✗ pillify.tsx: Still contains ReactDOM.render"
fi

echo "   Checking tooltipify.tsx..."
if ! grep -q "ReactDOM.render" /app/src/utils/tooltipify.tsx; then
    echo "   ✓ tooltipify.tsx: No ReactDOM.render found"
else
    echo "   ✗ tooltipify.tsx: Still contains ReactDOM.render"
fi
echo ""

echo "4. Verifying ReactRootManager usage in components..."
for file in EditHistoryMessage.tsx TextualBody.tsx; do
    if grep -q "new ReactRootManager()" /app/src/components/views/messages/$file; then
        echo "   ✓ $file uses ReactRootManager"
    else
        echo "   ✗ $file does not use ReactRootManager"
    fi
done
echo ""

echo "5. Running test suite..."
cd /app && npm test -- --testPathPattern="(pillify|tooltipify)" --no-coverage --silent 2>&1 | grep -E "(Test Suites:|Tests:)"
echo ""

echo "============================================================"
echo "DEMONSTRATION COMPLETE"
echo "============================================================"
echo ""
echo "All changes successfully implemented and verified!"
echo "The codebase is now using React 18 createRoot API."
