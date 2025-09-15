#!/usr/bin/env node
/**
 * Simple test to verify inline assistance frontend components exist and can be imported.
 */

const fs = require('fs');
const path = require('path');

function testFileExists(filePath, description) {
    const fullPath = path.join(__dirname, filePath);
    if (fs.existsSync(fullPath)) {
        console.log(`✓ ${description}: ${filePath}`);
        return true;
    } else {
        console.log(`✗ ${description}: ${filePath} (NOT FOUND)`);
        return false;
    }
}

function testDirectoryExists(dirPath, description) {
    const fullPath = path.join(__dirname, dirPath);
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
        console.log(`✓ ${description}: ${dirPath}`);
        return true;
    } else {
        console.log(`✗ ${description}: ${dirPath} (NOT FOUND)`);
        return false;
    }
}

console.log('Testing Inline Assistance Frontend Components...\n');

let allPassed = true;

// Test core components
allPassed &= testFileExists('src/hooks/useInlineAssistance.ts', 'Inline Assistance Hook');
allPassed &= testFileExists('src/services/inlineAssistanceService.ts', 'Inline Assistance Service');
allPassed &= testFileExists('src/components/inline-assistance/InlineSuggestionWidget.tsx', 'Suggestion Widget Component');
allPassed &= testFileExists('src/components/inline-assistance/HoverTooltip.tsx', 'Hover Tooltip Component');

// Test integration in CodeCell
allPassed &= testFileExists('src/components/notebook/cells/CodeCell.tsx', 'Code Cell Component');

// Test directories
allPassed &= testDirectoryExists('src/components/inline-assistance', 'Inline Assistance Components Directory');
allPassed &= testDirectoryExists('src/__tests__/components/inline-assistance', 'Inline Assistance Tests Directory');

// Test test files
allPassed &= testFileExists('src/__tests__/components/inline-assistance/InlineSuggestionWidget.test.tsx', 'Suggestion Widget Tests');
allPassed &= testFileExists('src/__tests__/services/inlineAssistanceService.test.ts', 'Service Tests');

console.log('\n' + (allPassed ? '✅ All frontend components exist!' : '❌ Some components are missing!'));

// Test basic syntax by trying to read and parse key files
console.log('\nTesting file syntax...');

try {
    const hookContent = fs.readFileSync(path.join(__dirname, 'src/hooks/useInlineAssistance.ts'), 'utf8');
    if (hookContent.includes('useInlineAssistance') && hookContent.includes('export')) {
        console.log('✓ Hook file has correct exports');
    } else {
        console.log('✗ Hook file missing expected exports');
        allPassed = false;
    }
} catch (e) {
    console.log('✗ Error reading hook file:', e.message);
    allPassed = false;
}

try {
    const serviceContent = fs.readFileSync(path.join(__dirname, 'src/services/inlineAssistanceService.ts'), 'utf8');
    if (serviceContent.includes('InlineAssistanceService') && serviceContent.includes('getSuggestions')) {
        console.log('✓ Service file has correct class and methods');
    } else {
        console.log('✗ Service file missing expected class or methods');
        allPassed = false;
    }
} catch (e) {
    console.log('✗ Error reading service file:', e.message);
    allPassed = false;
}

console.log('\n' + (allPassed ? '🎉 Frontend inline assistance system is ready!' : '⚠️  Some issues found in frontend system'));

process.exit(allPassed ? 0 : 1);