const fs = require('fs');
const vm = require('vm');

const jsPath = __dirname + '/generated_themes.js';

if (!fs.existsSync(jsPath)) {
  console.error('generated_themes.js not found!');
  process.exit(1);
}

const code = fs.readFileSync(jsPath, 'utf-8');
const sandbox = { window: {} };
try {
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  if (sandbox.window.availableThemes && Array.isArray(sandbox.window.availableThemes)) {
    console.log('✅ availableThemes loaded:', sandbox.window.availableThemes.length, 'themes found.');
    process.exit(0);
  } else {
    console.error('❌ availableThemes not loaded or not an array.');
    process.exit(2);
  }
} catch (e) {
  console.error('❌ Error evaluating generated_themes.js:', e);
  process.exit(3);
} 