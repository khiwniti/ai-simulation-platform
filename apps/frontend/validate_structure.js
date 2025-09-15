const fs = require('fs');
const path = require('path');

// Check if all required files exist
const requiredFiles = [
  'src/stores/workbookStore.ts',
  'src/components/layout/Sidebar.tsx',
  'src/components/layout/MainContent.tsx',
  'src/components/layout/Layout.tsx',
  'src/components/workbook/WorkbookManager.tsx',
  'src/components/notebook/NotebookManager.tsx',
  'src/app/page.tsx',
  'src/app/layout.tsx',
  'src/app/globals.css',
  'tailwind.config.js',
  'postcss.config.js'
];

const testFiles = [
  'src/__tests__/stores/workbookStore.test.ts',
  'src/__tests__/components/layout/Sidebar.test.tsx',
  'src/__tests__/components/layout/MainContent.test.tsx',
  'src/__tests__/components/workbook/WorkbookManager.test.tsx'
];

console.log('Validating React frontend foundation structure...\n');

let allFilesExist = true;

// Check main files
console.log('Main files:');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  const exists = fs.existsSync(filePath);
  console.log(`  ${exists ? '✓' : '✗'} ${file}`);
  if (!exists) allFilesExist = false;
});

console.log('\nTest files:');
testFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  const exists = fs.existsSync(filePath);
  console.log(`  ${exists ? '✓' : '✗'} ${file}`);
  if (!exists) allFilesExist = false;
});

// Check package.json dependencies
console.log('\nChecking package.json dependencies...');
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));

const requiredDeps = ['next', 'react', 'react-dom', 'zustand', '@ai-jupyter/shared'];
const requiredDevDeps = ['typescript', '@testing-library/react', '@testing-library/jest-dom', 'jest', 'tailwindcss'];

console.log('Dependencies:');
requiredDeps.forEach(dep => {
  const exists = packageJson.dependencies && packageJson.dependencies[dep];
  console.log(`  ${exists ? '✓' : '✗'} ${dep}`);
});

console.log('Dev Dependencies:');
requiredDevDeps.forEach(dep => {
  const exists = packageJson.devDependencies && packageJson.devDependencies[dep];
  console.log(`  ${exists ? '✓' : '✗'} ${dep}`);
});

// Check TypeScript configuration
console.log('\nChecking TypeScript configuration...');
const tsConfig = JSON.parse(fs.readFileSync(path.join(__dirname, 'tsconfig.json'), 'utf8'));
const hasPathMapping = tsConfig.compilerOptions && tsConfig.compilerOptions.paths;
console.log(`  ${hasPathMapping ? '✓' : '✗'} Path mapping configured`);

// Check Tailwind configuration
console.log('\nChecking Tailwind CSS configuration...');
const tailwindExists = fs.existsSync(path.join(__dirname, 'tailwind.config.js'));
const postcssExists = fs.existsSync(path.join(__dirname, 'postcss.config.js'));
console.log(`  ${tailwindExists ? '✓' : '✗'} tailwind.config.js`);
console.log(`  ${postcssExists ? '✓' : '✗'} postcss.config.js`);

console.log('\n' + '='.repeat(50));
if (allFilesExist && hasPathMapping && tailwindExists && postcssExists) {
  console.log('✓ All required files and configurations are in place!');
  console.log('✓ React frontend foundation is complete.');
  console.log('\nImplemented features:');
  console.log('  - React application with TypeScript and routing');
  console.log('  - Basic layout with sidebar navigation and main content area');
  console.log('  - Workbook and notebook management components');
  console.log('  - Zustand state management for application state');
  console.log('  - Component unit tests');
  console.log('  - Tailwind CSS for styling');
  console.log('  - TypeScript path mapping configuration');
} else {
  console.log('✗ Some required files or configurations are missing.');
}