#!/usr/bin/env node
/**
 * AutoHyperFlask Asset Build Configuration
 * Builds JavaScript bundle with esbuild
 */

const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

const isProduction = process.env.NODE_ENV === 'production';
const isWatch = process.argv.includes('--watch');

// Ensure output directory exists
const outdir = path.join(__dirname, 'public', 'dist');
if (!fs.existsSync(outdir)) {
  fs.mkdirSync(outdir, { recursive: true });
}

const buildOptions = {
  entryPoints: ['app/assets/main.js'],
  bundle: true,
  outdir: outdir,
  format: 'iife',
  platform: 'browser',
  target: ['es2020'],
  sourcemap: !isProduction,
  minify: isProduction,
  logLevel: 'info',
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
  },
};

async function build() {
  try {
    if (isWatch) {
      console.log('👀 Watching for changes...');
      const ctx = await esbuild.context(buildOptions);
      await ctx.watch();
    } else {
      console.log('🏗️  Building assets...');
      const result = await esbuild.build(buildOptions);
      console.log('✅ Build complete!');
      console.log(`   Output: ${outdir}/main.js`);
    }
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

build();
