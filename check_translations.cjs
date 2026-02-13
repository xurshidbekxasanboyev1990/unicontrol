const uz = require('./src/i18n/uz.js').default || require('./src/i18n/uz.js');
const ru = require('./src/i18n/ru.js').default || require('./src/i18n/ru.js');
const en = require('./src/i18n/en.js').default || require('./src/i18n/en.js');

function flattenObj(obj, prefix) {
  prefix = prefix || '';
  var result = {};
  for (var k in obj) {
    var key = prefix ? prefix + '.' + k : k;
    if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
      Object.assign(result, flattenObj(obj[k], key));
    } else {
      result[key] = obj[k];
    }
  }
  return result;
}

var uzFlat = flattenObj(uz);
var ruFlat = flattenObj(ru);
var enFlat = flattenObj(en);

// Check for RU values same as UZ (potential untranslated Uzbek text in Russian)
console.log('=== RU values same as UZ (Uzbek text left in Russian file) ===');
var ruSameAsUz = 0;
Object.keys(uzFlat).forEach(function(k) {
  if (ruFlat[k] && typeof uzFlat[k] === 'string' && typeof ruFlat[k] === 'string') {
    if (uzFlat[k] === ruFlat[k] && uzFlat[k].length > 5) {
      var val = uzFlat[k];
      // Check contains Latin (Uzbek) but not Cyrillic
      var hasCyrillic = /[\u0400-\u04FF]/.test(val);
      var isPlainEnglish = /^[A-Za-z0-9\s\.\,\!\?\-\+\@\#\$\%\(\)\[\]\{\}\/\\:\"\'~_\*\&\=\<\>]+$/.test(val);
      if (!hasCyrillic && !isPlainEnglish) {
        console.log('  ', k, ':', JSON.stringify(val));
        ruSameAsUz++;
      }
    }
  }
});
console.log('Total:', ruSameAsUz);

// Check for EN values same as UZ 
console.log('\n=== EN values same as UZ (Uzbek text left in English file) ===');
var enSameAsUz = 0;
Object.keys(uzFlat).forEach(function(k) {
  if (enFlat[k] && typeof uzFlat[k] === 'string' && typeof enFlat[k] === 'string') {
    if (uzFlat[k] === enFlat[k] && uzFlat[k].length > 5) {
      var val = uzFlat[k];
      var hasCyrillic = /[\u0400-\u04FF]/.test(val);
      var isPlainEnglish = /^[A-Za-z0-9\s\.\,\!\?\-\+\@\#\$\%\(\)\[\]\{\}\/\\:\"\'~_\*\&\=\<\>]+$/.test(val);
      if (!hasCyrillic && !isPlainEnglish) {
        console.log('  ', k, ':', JSON.stringify(val));
        enSameAsUz++;
      }
    }
  }
});
console.log('Total:', enSameAsUz);

// Check for EN values same as RU (Russian text left in English file)
console.log('\n=== EN values same as RU (Russian text in English file) ===');
var enSameAsRu = 0;
Object.keys(ruFlat).forEach(function(k) {
  if (enFlat[k] && typeof ruFlat[k] === 'string' && typeof enFlat[k] === 'string') {
    if (ruFlat[k] === enFlat[k] && /[\u0400-\u04FF]/.test(ruFlat[k])) {
      console.log('  ', k, ':', JSON.stringify(ruFlat[k]));
      enSameAsRu++;
    }
  }
});
console.log('Total:', enSameAsRu);

// Check landing.heroTitle3 empty in RU
console.log('\n=== EMPTY VALUES ===');
console.log('ru landing.heroTitle3:', JSON.stringify(ruFlat['landing.heroTitle3']));
console.log('uz landing.heroTitle3:', JSON.stringify(uzFlat['landing.heroTitle3']));
console.log('en landing.heroTitle3:', JSON.stringify(enFlat['landing.heroTitle3']));

// Check for RU values that contain English text (should be Russian)
console.log('\n=== RU values that look English (no Cyrillic, long text) ===');
var ruEnglish = 0;
Object.keys(ruFlat).forEach(function(k) {
  if (typeof ruFlat[k] === 'string' && ruFlat[k].length > 10) {
    var hasCyrillic = /[\u0400-\u04FF]/.test(ruFlat[k]);
    var hasUzSpecific = /[\']/g;
    // Skip known English/brand names
    var skipKeys = ['settings.uzbek', 'settings.russian', 'settings.english', 'telegram.chatId', 'layout.market'];
    if (!hasCyrillic && !skipKeys.includes(k)) {
      var val = ruFlat[k];
      // Skip if it's a format string with only variables
      if (!/^[\{\}\d\s\%\.\,\-\/\(\)]+$/.test(val)) {
        console.log('  ', k, ':', JSON.stringify(val));
        ruEnglish++;
      }
    }
  }
});
console.log('Total:', ruEnglish);

// Check for EN values that contain Cyrillic (should be English)
console.log('\n=== EN values that contain Cyrillic (should be English) ===');
var enCyrillic = 0;
Object.keys(enFlat).forEach(function(k) {
  if (typeof enFlat[k] === 'string' && /[\u0400-\u04FF]/.test(enFlat[k])) {
    // Skip language name keys
    var skipKeys = ['settings.uzbek', 'settings.russian'];
    if (!skipKeys.includes(k)) {
      console.log('  ', k, ':', JSON.stringify(enFlat[k]));
      enCyrillic++;
    }
  }
});
console.log('Total:', enCyrillic);
