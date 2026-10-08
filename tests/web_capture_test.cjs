/* Capture inputs and native-state provenance must survive malformed authoring. */
const assert=require('node:assert/strict');
const {rowsFromCsv,checkStateIdentity}=require('../scripts/quality/capture_web_core.cjs');
assert.deepEqual(rowsFromCsv('1,8\r\n0,600\r\n'),[[1,8],[0,600]]);
assert.deepEqual(rowsFromCsv('1023,36000'),[[1023,36000]]);
for (const value of ['', 'frame,keys', '1,0', '-1,8', '1024,8', '1,36001', '1,8,0', '1,NaN'])
  assert.throws(()=>rowsFromCsv(value),undefined,value);
assert.throws(()=>rowsFromCsv(Array(17).fill('0,36000').join('\n')),/bounds/);
const metadata={rom_sha256:'verified-rom',mgba_revision:'26b7884bc25a5933960f3cdcd98bac1ae14d42e2',controller_only:true};
checkStateIdentity(metadata,'verified-rom');
assert.throws(()=>checkStateIdentity(metadata,'other-rom'),/different cartridge/);
assert.throws(()=>checkStateIdentity({...metadata,mgba_revision:'different-core'},'verified-rom'),/core revision/);
assert.throws(()=>checkStateIdentity({...metadata,controller_only:false},'verified-rom'),/provenance/);
console.log('WASM capture bounds and exact-cartridge/core state provenance passed.');
