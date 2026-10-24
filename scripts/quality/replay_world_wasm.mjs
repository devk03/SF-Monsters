/** Replay actual controller input against the website's pinned WASM core.
 * This is deterministic guest-state verification, not browser performance QA.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const args=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,list)=>{
    if(i%2===0)a.push([v.replace(/^--/,''),list[i+1]]);return a;
},[]));
for(const key of ['native-dir','initial-state','battery','rom','output'])
    if(!args[key])throw Error('Required --'+key);
const source=path.resolve(args['native-dir']),output=path.resolve(args.output);
if(!output.startsWith(path.join(root,'.tools')+path.sep))throw Error('Keep captures private under .tools');
fs.mkdirSync(output,{recursive:false});
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const read=filename=>fs.readFileSync(path.resolve(filename));
const session=JSON.parse(read(path.join(source,'session.json')));
const rom=read(args.rom),state=read(args['initial-state']),battery=read(args.battery);
if(!session.controller_only||session.rom_sha256!==digest(rom)
    ||session.state_input_sha256!==digest(state)||session.battery_input_sha256!==digest(battery))
    throw Error('Replay inputs differ from actual native session identity');
const native=read(path.join(source,args['final-state']||'returned.state'));
const rows=JSON.parse(read(path.join(source,'inputs.json')));
let frames=0;
for(const row of rows){
    if(!Array.isArray(row)||row.length!==2||!row.every(Number.isSafeInteger)
        ||row[0]<0||row[0]>1023||row[1]<1||row[1]>36000)throw Error('Invalid native controller input');
    frames+=row[1];
}
if(frames<1||frames>900000)throw Error('Replay exceeds finite frame bound');
const core=path.join(root,'web/public/emulator');
const build=JSON.parse(read(path.join(core,'core-build.json')));
for(const [filename,hash] of Object.entries(build.artifacts))
    if(digest(read(path.join(core,filename)))!==hash)throw Error('Pinned core changed: '+filename);
const modulePath=path.join(output,'mgba-core.cjs');
fs.copyFileSync(path.join(core,'mgba.js'),modulePath);
const factory=createRequire(import.meta.url)(modulePath);
const mod=await factory({wasmBinary:read(path.join(core,'mgba.wasm')),
    printErr:line=>{if(/error|fatal/i.test(line))process.stderr.write(line+'\n');}});
const allocate=bytes=>{const p=mod._malloc(bytes.length);if(!p)throw Error('Core allocation failed');mod.HEAPU8.set(bytes,p);return p;};
mod._mgbawasm_init();
const cartridge=allocate(rom);
if(!mod._mgbawasm_load(cartridge,rom.length,0,0,0,0,1))throw Error('ROM load failed');
mod._free(cartridge);
let pointer=allocate(battery);
if(!mod._mgbawasm_sram_load(pointer,battery.length))throw Error('Battery load failed');
mod._free(pointer);
pointer=allocate(state);
if(!mod._mgbawasm_state_load(pointer))throw Error('Initial native state load failed');
mod._free(pointer);
const deadline=Date.now()+20*60*1000;
for(const [keys,count] of rows){
    if(Date.now()>deadline)throw Error('Replay reached finite20minute deadline');
    mod._mgbawasm_set_keys(keys);
    for(let i=0;i<count;i++)mod._mgbawasm_run_frame();
}
const size=mod._mgbawasm_state_size();pointer=mod._malloc(size);
mod.HEAPU8.fill(0,pointer,pointer+size);
if(mod._mgbawasm_state_save(pointer)!==1)throw Error('Final state serialization failed');
const actual=Buffer.from(mod.HEAPU8.slice(pointer,pointer+size));mod._free(pointer);
fs.writeFileSync(path.join(output,'capture.state'),actual);
if(native.length!==0x61000||actual.length!==native.length)throw Error('Unsupported native state geometry');
const left=native.subarray(0x19000),right=actual.subarray(0x19000);
const different=left.reduce((count,value,i)=>count+Number(value!==right[i]),0);
const trace=rows.map(row=>row.join(',')+'\n').join('');
const capture={controller_only:true,rom_sha256:digest(rom),mgba_revision:build.mgba_revision,
    state_input_sha256:digest(state),battery_input_sha256:digest(battery),input_sha256:digest(trace),frames};
fs.writeFileSync(path.join(output,'capture.json'),JSON.stringify(capture,null,2)+'\n');
const result={passed:different===0,rom_sha256:digest(rom),frames,ram_bytes:left.length,
    different_bytes:different,native_ram_sha256:digest(left),wasm_ram_sha256:digest(right),
    scope:'Exact native-controller input/state/Flash replay in the website core; not browser timing/audio acceptance'};
fs.writeFileSync(path.join(output,'wasm-result.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
if(different)process.exitCode=1;
