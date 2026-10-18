// Parse executable inline scripts and structured data before deployment.
const fs = require('node:fs');
const vm = require('node:vm');
const files = ['index.html', 'admin/index.html', 'reviews/index.html',
  'services/nationwide-daeri/index.html', 'services/nationwide-transport/index.html'];
let count = 0;
for (const file of files) {
  const html = fs.readFileSync(file, 'utf8');
  for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    const [, attributes, body] = match;
    if (!body.trim()) continue;
    if (/type=["']application\/ld\+json["']/i.test(attributes)) JSON.parse(body);
    else new vm.Script(body, {filename: file});
    count++;
  }
}
console.log(`JavaScript and structured data validation passed: ${files.length} pages, ${count} scripts.`);
