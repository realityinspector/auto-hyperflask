#!/usr/bin/env node
/**
 * Copy Bootstrap Icons to public directory
 */

const fs = require('fs');
const path = require('path');

const sourceDir = path.join(__dirname, '../node_modules/bootstrap-icons/font');
const targetDir = path.join(__dirname, '../public/bootstrap-icons');

// Create target directory if it doesn't exist
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

// Copy files
const files = ['bootstrap-icons.css', 'fonts'];

console.log('📦 Copying Bootstrap Icons...');

files.forEach(file => {
  const source = path.join(sourceDir, file);
  const target = path.join(targetDir, file);

  if (fs.existsSync(source)) {
    if (fs.lstatSync(source).isDirectory()) {
      // Copy directory recursively
      if (!fs.existsSync(target)) {
        fs.mkdirSync(target, { recursive: true });
      }
      const dirFiles = fs.readdirSync(source);
      dirFiles.forEach(f => {
        fs.copyFileSync(path.join(source, f), path.join(target, f));
      });
      console.log(`  ✓ Copied ${file}/ directory`);
    } else {
      // Copy file
      fs.copyFileSync(source, target);
      console.log(`  ✓ Copied ${file}`);
    }
  }
});

console.log('✅ Bootstrap Icons copied successfully!');
