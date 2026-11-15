import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const source = new URL('./', import.meta.url);
export const submittedSHA256 = 'd14587873861e81318e9a726b04b581efbc9c58795c8e9bad675ea0ceba7dfc3';
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

async function text(relative) {
  return (await readFile(new URL(relative, source), 'utf8')).replaceAll('\r\n', '\n');
}

async function templateScript() {
  const template = JSON.parse(await text('assets/workbuddy.json'));
  const avatars = {};
  for (const name of ['team', 'team-lead', 'production', 'review']) {
    const bytes = await readFile(new URL('assets/icons/' + name + '.png', source));
    avatars[name] = bytes.toString('base64');
  }
  const shell = await text('web/template.js.in');
  return shell.replace('__WORKBUDDY_TEMPLATE__', () => JSON.stringify({ ...template, avatars }));
}

export async function modulesInOrder() {
  const html = await text('web/index.html');
  const pattern = /<script src="([a-z][a-z0-9-]*\.js)" defer><\/script>/g;
  const names = [...html.matchAll(pattern)].map(match => match[1]);
  if (new Set(names).size !== names.length || !names.includes('template.js') || names.at(-1) !== 'app.js') {
    throw Error('Expected unique local scripts, a WorkBuddy template, and the UI entry last.');
  }
  const scripts = [];
  for (const name of names) {
    const code = name === 'template.js' ? await templateScript() : await text('web/' + name);
    if (/<\/script/i.test(code)) throw Error('Unsafe closing script tag in ' + name);
    scripts.push({ name, code });
  }
  return { html, pattern, scripts };
}

export async function build() {
  const { html, pattern, scripts } = await modulesInOrder();
  const css = await text('web/builder.css');
  const cspHash = code => "'sha256-" + createHash('sha256').update(code).digest('base64') + "'";
  const embedded = scripts.map(({ code }) => '<script>' + code + '</script>').join('');
  return html
    .replace('<link rel="stylesheet" href="builder.css">', () => '<style>' + css + '</style>')
    .replace(pattern, '')
    .replace('</body>', () => embedded + '</body>')
    .replace("style-src 'self'", () => 'style-src ' + cspHash(css))
    .replace("script-src 'self'", () => 'script-src ' + scripts.map(({ code }) => cspHash(code)).join(' '));
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const [arg, ...extra] = process.argv.slice(2);
  if (extra.length) throw Error('Usage: node build.mjs [new-output.html | --check]');
  const bytes = Buffer.from(await build());
  const actual = sha256(bytes);
  if (arg === '--check') {
    if (actual !== submittedSHA256) throw Error('Submission differs: ' + actual);
    console.log(actual + '  exact 0.2.2b submission');
  } else {
    const output = arg || 'team-builder.html';
    try {
      await writeFile(output, bytes, { flag: 'wx' });
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
      if (!(await readFile(output)).equals(bytes)) {
        throw Error('A different file exists. Choose a new output name: ' + output);
      }
    }
    console.log(actual + '  ' + output);
  }
}
