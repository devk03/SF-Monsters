/* Controller-only captures using the exact pinned browser core, without Docker. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const {once} = require('node:events');
const {execFileSync} = require('node:child_process');
const ROOT = path.resolve(__dirname, '../..');
const RUNTIME = path.join(ROOT, 'web/public/emulator');
const REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2';
const BASE_HASH = 'a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af';
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function rowsFromCsv(text) {
  let total = 0;
  const rows = text.trim().split(/\r?\n/).map(line => {
    if (!/^\d+,\d+$/.test(line)) throw new Error('Use keys,duration controller rows.');
    const [keys, frames] = line.split(',').map(Number);
    total += frames;
    if (keys >= 1024 || frames < 1 || frames > 36000 || total > 600000)
      throw new Error('Controller input exceeds native capture bounds.');
    return [keys, frames];
  });
  return rows;
}

function matchingManifest(digest) {
  if (digest === BASE_HASH) return null;
  const roots = [path.join(ROOT, 'romhack/releases'), path.join(ROOT, '.tools/romhack-drafts')];
  function visit(directory, depth) {
    if (!fs.existsSync(directory)) return null;
    for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
      const filename = path.join(directory, entry.name);
      if (entry.isDirectory() && depth > 0) {
        const found = visit(filename, depth - 1); if (found) return found;
      } else if (entry.isFile() && entry.name === 'manifest.json') {
        const manifest = JSON.parse(fs.readFileSync(filename, 'utf8'));
        if (manifest.target_sha256 === digest) return manifest;
      }
    }
    return null;
  }
  for (const root of roots) {const manifest = visit(root, 2); if (manifest) return manifest;}
  throw new Error('Use the verified reference or a manifest-verified SF cartridge.');
}

function checkStateIdentity(metadata, digest) {
  if (metadata.rom_sha256 !== digest || metadata.mgba_revision !== REVISION)
    throw new Error('State belongs to a different cartridge or core revision.');
  if (metadata.controller_only !== true)
    throw new Error('State needs its controller-only provenance metadata.');
}

async function loadCore() {
  const build = JSON.parse(fs.readFileSync(path.join(RUNTIME, 'core-build.json'), 'utf8'));
  if (build.mgba_revision !== REVISION) throw new Error('Browser core revision mismatch.');
  for (const name of ['mgba.js', 'mgba.wasm'])
    if (hash(fs.readFileSync(path.join(RUNTIME, name))) !== build.artifacts[name])
      throw new Error('Browser core artifact fingerprint mismatch.');
  const sandbox = {require, process, console, __dirname:RUNTIME, __filename:path.join(RUNTIME,'mgba.js'),
    exports:{}, module:{exports:{}}, TextDecoder, TextEncoder, WebAssembly,
    Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array,
    Float32Array, Float64Array, ArrayBuffer, setTimeout, clearTimeout};
  vm.runInNewContext(fs.readFileSync(path.join(RUNTIME,'mgba.js'),'utf8'),sandbox);
  return sandbox.module.exports({wasmBinary:fs.readFileSync(path.join(RUNTIME,'mgba.wasm'))});
}

async function capture(options) {
  if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(options.name)) throw new Error('Use a short new benchmark name.');
  if (options.state && options.battery) throw new Error('Choose a state or battery, not both.');
  const rom = fs.readFileSync(options.rom), digest = hash(rom), manifest = matchingManifest(digest);
  if (rom.length !== 16777216 || rom.subarray(0xac,0xb0).toString() !== 'BPEE')
    throw new Error('This harness records verified Emerald-family cartridges.');
  const input = fs.readFileSync(options.input, 'utf8'), rows = rowsFromCsv(input);
  const state = options.state ? fs.readFileSync(options.state) : null;
  if (state) checkStateIdentity(JSON.parse(fs.readFileSync(options.state.replace(/\.state$/,'.json'),'utf8')),digest);
  const companion = options.state?.replace(/\.state$/,'.sav');
  const batteryPath = options.battery || (companion && fs.existsSync(companion) ? companion : null);
  const battery = batteryPath ? fs.readFileSync(batteryPath) : null;
  if (battery && battery.length !== 131072) throw new Error('Expected a 128 KiB Flash battery.');
  const output = path.join(ROOT,'.tools/benchmarks',options.name);
  if (fs.existsSync(output)) throw new Error('Existing evidence is preserved; choose a new name.');
  const core = await loadCore();
  core._mgbawasm_init();
  function transfer(bytes, operation) {
    const address = core._malloc(bytes.length);
    try {core.HEAPU8.set(bytes,address); if (!operation(address,bytes.length)) throw new Error('Core rejected input.');}
    finally {core._free(address);}
  }
  transfer(rom,(address,length)=>core._mgbawasm_load(address,length,0,0,0,0,1));
  core._mgbawasm_run_frame();
  if (battery) {
    transfer(battery,(address,length)=>core._mgbawasm_sram_load(address,length));
    core._mgbawasm_reset(); core._mgbawasm_run_frame();
  }
  if (state) {
    if (state.length !== core._mgbawasm_state_size()) throw new Error('State size mismatch.');
    transfer(state,address=>core._mgbawasm_state_load(address));
  }
  fs.mkdirSync(output);
  const filename = extension => path.join(output,'capture.'+extension);
  const audio = fs.openSync(filename('pcm'),'wx'), trace = fs.openSync(filename('csv'),'wx');
  const audioPointer = core._malloc(8192*4);
  let audioSamples=0, audioPeak=0, frames=0;
  function drain(record) {
    while (core._mgbawasm_audio_available()>0) {
      const count=core._mgbawasm_read_audio(audioPointer,8192);
      if (!count) throw new Error('Audio queue could not drain.');
      if (record) {
        const bytes=Buffer.from(core.HEAPU8.subarray(audioPointer,audioPointer+count*4));
        fs.writeSync(audio,bytes); audioSamples+=count;
        for (let i=0;i<bytes.length;i+=2) audioPeak=Math.max(audioPeak,Math.abs(bytes.readInt16LE(i)));
      }
    }
  }
  drain(false); // Match native capture's boundary after initial/reset/state alignment.
  let gzip=null, videoFile=null;
  const videoHash=crypto.createHash('sha256');
  if (options.video) {
    gzip=zlib.createGzip({level:9}); videoFile=fs.createWriteStream(filename('rgba'),{flags:'wx'});
    gzip.pipe(videoFile);
  }
  fs.writeSync(trace,'frame,keys\n');
  try {
    for (const [keys,duration] of rows) {
      core._mgbawasm_set_keys(keys);
      for (let n=0;n<duration;n++) {
        core._mgbawasm_run_frame(); frames++; drain(true);
        fs.writeSync(trace,`${core._mgbawasm_frame_counter()},${keys}\n`);
        if (gzip) {
          const address=core._mgbawasm_video_ptr();
          const pixels=Buffer.from(core.HEAPU8.subarray(address,address+240*160*4));
          videoHash.update(pixels);
          if (!gzip.write(pixels)) await once(gzip,'drain');
        }
      }
    }
    if (gzip) {gzip.end(); await once(videoFile,'finish');}
  } finally {fs.closeSync(audio); fs.closeSync(trace); core._free(audioPointer);}
  const statePointer=core._malloc(core._mgbawasm_state_size());
  try {
    if (!core._mgbawasm_state_save(statePointer)) throw new Error('Could not export the actual core state.');
    fs.writeFileSync(filename('state'),Buffer.from(core.HEAPU8.subarray(statePointer,statePointer+core._mgbawasm_state_size())));
  } finally {core._free(statePointer);}
  const length=core._mgbawasm_sram_save(), address=core._mgbawasm_sram_ptr();
  fs.writeFileSync(filename('sav'),Buffer.from(core.HEAPU8.subarray(address,address+length)));
  const pixels=core._mgbawasm_video_ptr();
  fs.writeFileSync(filename('final.rgba'),Buffer.from(core.HEAPU8.subarray(pixels,pixels+240*160*4)));
  const metadata={frames,frequency:16777216,frame_cycles:280896,sample_rate:core._mgbawasm_sample_rate(),
    audio_samples:audioSamples,audio_peak:audioPeak,width:240,height:160,rom_sha256:digest,game_code:'BPEE',
    runtime:'WebAssembly mGBA 0.10.5 core, Node controller harness',mgba_revision:REVISION,
    controller_only:true,trace_only:!options.video,input_sha256:hash(Buffer.from(input)),
    battery_input_sha256:battery?hash(battery):null,state_input_sha256:state?hash(state):null,
    source_commit:execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim(),
    source_worktree_dirty:!!execFileSync('git',['status','--porcelain'],{cwd:ROOT,encoding:'utf8'}).trim(),
    fixture:manifest?.fixture||null,user_quality_approval:'pending',host_browser_performance_proven:false};
  if (options.video) metadata.video_storage={encoding:'gzip',sha256:videoHash.digest('hex'),bytes:frames*240*160*4};
  fs.writeFileSync(filename('json'),JSON.stringify(metadata,null,2)+'\n');
  console.log(`WASM controller capture: ${frames} frames, ${audioSamples} stereo pairs. ${output}`);
  return output;
}

function argumentsFrom(argv) {
  const options={};
  for (let i=0;i<argv.length;i++) {
    if (argv[i]==='--video') {options.video=true;continue;}
    const key=argv[i].replace(/^--/,'');
    if (!['rom','input','name','state','battery'].includes(key) || !argv[i+1] || options[key])
      throw new Error('Use --rom PATH --input CSV --name NAME [--state PATH | --battery PATH] [--video].');
    options[key]=argv[++i];
  }
  if (!options.rom||!options.input||!options.name) throw new Error('ROM, input and a new output name are required.');
  return options;
}
module.exports={capture,rowsFromCsv,checkStateIdentity};
if (require.main===module) capture(argumentsFrom(process.argv.slice(2))).catch(error=>{
  console.error(error.message);process.exitCode=1;
});
