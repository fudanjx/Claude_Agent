#!/bin/bash
# Verification script for Claude Skills System installation

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Claude Skills System - Installation Verification          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        return 1
    fi
}

echo "Checking files..."
echo ""

# Core files
echo "Core Implementation:"
check_file "skill_loader.py"
check_file "config.py"
check_file "lead_agent.py"
check_file "prompts.py"
check_file "requirements.txt"
echo ""

# Skills directory
echo "Skills Directory:"
check_dir "skills"
check_file "skills/SKILLS.md"
check_file "skills/README.md"
check_dir "skills/web-research"
check_file "skills/web-research/SKILL.md"
echo ""

# Test suite
echo "Test Suite:"
check_file "test_skills_integration.py"
if [ -x "test_skills_integration.py" ]; then
    echo -e "${GREEN}✓${NC} test_skills_integration.py is executable"
else
    echo -e "${YELLOW}⚠${NC} test_skills_integration.py is not executable (run: chmod +x test_skills_integration.py)"
fi
echo ""

# Documentation
echo "Documentation:"
check_file "SKILLS_IMPLEMENTATION.md"
check_file "IMPLEMENTATION_COMPLETE.md"
check_file "SKILLS_ARCHITECTURE.md"
check_file "IMPLEMENTATION_CHECKLIST.md"
echo ""

# Check Python dependencies
echo "Checking Python dependencies..."
if python3 -c "import yaml" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pyyaml installed"
else
    echo -e "${RED}✗${NC} pyyaml not installed (run: pip3 install pyyaml)"
    exit 1
fi

if python3 -c "import boto3" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} boto3 installed"
else
    echo -e "${RED}✗${NC} boto3 not installed (run: pip3 install -r requirements.txt)"
    exit 1
fi
echo ""

# Test skill loader
echo "Testing skill loader module..."
if python3 -c "from skill_loader import SkillLoader; from pathlib import Path; loader = SkillLoader(Path('skills')); skills = loader.discover_skills(); assert len(skills) > 0" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Skill loader works"
else
    echo -e "${RED}✗${NC} Skill loader failed"
    exit 1
fi
echo ""

# Run test suite
echo "Running test suite..."
echo "────────────────────────────────────────────────────────────────"
if python3 test_skills_integration.py; then
    echo "────────────────────────────────────────────────────────────────"
    echo -e "${GREEN}✓${NC} All tests passed!"
else
    echo "────────────────────────────────────────────────────────────────"
    echo -e "${RED}✗${NC} Tests failed"
    exit 1
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    VERIFICATION COMPLETE                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Claude Skills System is correctly installed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Try it: python3 lead_agent.py \"Research Python frameworks\""
echo "  2. Create a skill: mkdir -p skills/my-skill"
echo "  3. Read docs: IMPLEMENTATION_COMPLETE.md"
echo ""
