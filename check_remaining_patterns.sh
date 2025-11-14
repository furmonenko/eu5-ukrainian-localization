#!/bin/bash
cd /Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english

echo "Перевірка старих форматів які залишились:"
echo "=========================================="

for pattern in pops war army market province religion culture character ruler building food trade merchants; do
    count=$(find . -name "*.yml" -type f -exec grep -o "\[${pattern}|e\]" {} \; 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
        echo "$count - [${pattern}|e]"
    fi
done | sort -rn
