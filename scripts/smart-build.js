#!/usr/bin/env node
/**
 * Smart build script that only rebuilds when source files have changed
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const CACHE_FILE = path.join(__dirname, '../.build-cache.json');

// Files to watch for changes
const SOURCE_FILES = [
  'app/assets/main.js',
  'app/assets/main.css',
  'build.js',
  'tailwind.config.js',
  'package.json',
];

// Directories to scan for template changes
const TEMPLATE_DIRS = [
  'app/pages',
  'app/templates',
];

/**
 * Calculate hash of a file
 */
function hashFile(filePath) {
  try {
    const content = fs.readFileSync(filePath);
    return crypto.createHash('md5').update(content).digest('hex');
  } catch (error) {
    return null;
  }
}

/**
 * Get all files in a directory recursively
 */
function getAllFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;

  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      getAllFiles(filePath, fileList);
    } else if (file.endsWith('.jpy') || file.endsWith('.html')) {
      fileList.push(filePath);
    }
  });
  return fileList;
}

/**
 * Calculate hash of all source files
 */
function calculateSourceHash() {
  const hashes = {};

  // Hash individual source files
  SOURCE_FILES.forEach(file => {
    const hash = hashFile(file);
    if (hash) hashes[file] = hash;
  });

  // Hash template files
  TEMPLATE_DIRS.forEach(dir => {
    const files = getAllFiles(dir);
    files.forEach(file => {
      const hash = hashFile(file);
      if (hash) hashes[file] = hash;
    });
  });

  // Create combined hash
  const combinedHash = crypto.createHash('md5')
    .update(JSON.stringify(hashes))
    .digest('hex');

  return { individual: hashes, combined: combinedHash };
}

/**
 * Load previous build cache
 */
function loadCache() {
  try {
    const cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
    return cache;
  } catch (error) {
    return null;
  }
}

/**
 * Save build cache
 */
function saveCache(hashes) {
  fs.writeFileSync(CACHE_FILE, JSON.stringify({
    timestamp: new Date().toISOString(),
    hashes: hashes,
  }, null, 2));
}

/**
 * Check if build is needed
 */
function needsBuild() {
  // Check if build outputs exist
  const outputs = [
    'public/dist/main.js',
    'public/dist/main.css',
    'public/bootstrap-icons/bootstrap-icons.css',
  ];

  const outputsExist = outputs.every(file => fs.existsSync(file));
  if (!outputsExist) {
    console.log('📦 Build outputs missing, build required');
    return true;
  }

  // Calculate current source hash
  const currentHashes = calculateSourceHash();

  // Load previous cache
  const cache = loadCache();
  if (!cache) {
    console.log('📦 No build cache found, build required');
    return true;
  }

  // Compare hashes
  if (currentHashes.combined !== cache.hashes.combined) {
    console.log('📦 Source files changed, build required');
    // Show what changed
    Object.keys(currentHashes.individual).forEach(file => {
      if (currentHashes.individual[file] !== cache.hashes.individual[file]) {
        console.log(`   Changed: ${file}`);
      }
    });
    return true;
  }

  console.log('✅ No changes detected, skipping build');
  return false;
}

/**
 * Run build
 */
function runBuild() {
  console.log('🚀 Running build...');
  try {
    execSync('npm run build:all', { stdio: 'inherit' });

    // Save cache after successful build
    const hashes = calculateSourceHash();
    saveCache(hashes);

    console.log('✅ Build complete and cached!');
    return true;
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    return false;
  }
}

// Main execution
if (require.main === module) {
  const force = process.argv.includes('--force');

  if (force) {
    console.log('⚡ Force build requested');
    runBuild();
  } else if (needsBuild()) {
    runBuild();
  }
}

module.exports = { needsBuild, runBuild, calculateSourceHash };
