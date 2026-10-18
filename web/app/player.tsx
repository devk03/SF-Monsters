'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { countCaught, decodeSave, encodeSave, nextQuest, readProgress, validateSave, type Progress } from './save-format';
import {flashCounter, validateSfFlashSave} from './flash-save';
import {patchLocalRom} from './rom-loader';

type Engine = {
  start(): void; pause(): void; resume(): void; destroy(): void;
  exportBattery(): Uint8Array; importBattery(bytes: Uint8Array): void;
  config: { write(key: string, value: number | boolean): boolean };
};
type Account = { id: string; name: string } | null;
declare global { interface Window {
  sfMiniMonstersLoad?: (config: unknown) => Promise<Engine>;
  sfMiniMonstersExtract?: (bytes: Uint8Array) => Promise<{bytes: Uint8Array}>;
} }
let runtimeLoader: Promise<void> | null = null;
function loadRuntime(): Promise<void> {
  if (runtimeLoader) return runtimeLoader;
  runtimeLoader = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.type = 'module'; script.src = '/emulator/entry.js';
    script.onload = () => resolve();
    script.onerror = () => { runtimeLoader = null; reject(new Error('The emulator could not be loaded. Try again.')); };
    document.head.appendChild(script);
  });
  return runtimeLoader;
}
const MAPS = ['Outer Sunset', 'SoMa / South Park', 'Cognition Lab'];
const ROUTE = [
  { flag: 2, label: 'Recover the prototype' },
  { flag: 4, label: 'Find Roon' },
  { flag: 8, label: 'Deliver to Cognition' },
  { flag: 32, label: 'Repair the safety relays' },
  { flag: 64, label: 'Earn the Build Badge' },
];
export default function GamePlayer({ account, signInUrl, signOutUrl, variant = 'emerald' }: {
  account: Account; signInUrl: string; signOutUrl: string; variant?: 'emerald' | 'prototype' | 'world';
}) {
  const legacy = variant === 'prototype';
  const world = variant === 'world';
  const edition = world ? 'world' : 'emerald';
  const fileStem = world ? 'sf-mini-monsters-world' : 'sf-mini-monsters';
  const canvas = useRef<HTMLCanvasElement>(null);
  const screenStage = useRef<HTMLDivElement>(null);
  const [displayWidth, setDisplayWidth] = useState(480);
  const [compactDisplay, setCompactDisplay] = useState(false);
  const [showGamepad, setShowGamepad] = useState(false);
  useEffect(() => {
    if (!world || !screenStage.current) return;
    const node = screenStage.current;
    const resize = () => setDisplayWidth(240 * Math.max(1, Math.min(
      compactDisplay ? 2 : 4, Math.floor((node.clientWidth - 24) / 240))));
    const observer = new ResizeObserver(resize); observer.observe(node); resize();
    return () => observer.disconnect();
  }, [world, compactDisplay]);
  const engine = useRef<Engine | null>(null);
  const importInput = useRef<HTMLInputElement>(null);
  const romInput = useRef<HTMLInputElement>(null);
  const [romBytes, setRomBytes] = useState<Uint8Array | null>(null);
  const [romUrl, setRomUrl] = useState<string | null>(null);
  const [phase, setPhase] = useState<'waiting' | 'verifying' | 'loading' | 'ready' | 'error'>(legacy ? 'loading' : 'waiting');
  const [notice, setNotice] = useState(legacy ? 'Loading your cartridge…' : 'Load your Emerald ROM. It stays on your device.');
  const [progress, setProgress] = useState<Progress | null>(null);
  const [paused, setPaused] = useState(false);
  const [muted, setMuted] = useState(false);
  const mutedRef = useRef(false);
  const [help, setHelp] = useState(false);
  const [backupUrl, setBackupUrl] = useState<string | null>(null);
  useEffect(() => () => { if (backupUrl) URL.revokeObjectURL(backupUrl); }, [backupUrl]);
  const [retry, setRetry] = useState(0);
  const storageKey = `sf-mini-monsters:${legacy ? 'v1' : world ? 'world:v1' : 'emerald:v2'}:${account?.id ?? 'guest'}`;
  const validateBattery = useCallback((bytes: Uint8Array) => {
    if (legacy) validateSave(bytes); else validateSfFlashSave(bytes, edition);
  }, [legacy, edition]);
  const batteryProgress = useCallback((bytes: Uint8Array): Progress | null => {
    if (legacy) return readProgress(bytes);
    try { validateSfFlashSave(bytes, edition); } catch { return null; }
    const sequence = flashCounter(bytes);
    return sequence === null ? null : {sequence, flags: 0, caught: 0, coins: 0, map: 0, party: 0};
  }, [legacy, edition]);
  useEffect(() => {
    if (!romBytes) return;
    const url = URL.createObjectURL(new Blob([new Uint8Array(romBytes)]));
    setRomUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [romBytes]);
  const lastSequence = useRef(-1);
  const heldKeys = useRef(new Set<string>());
  const sendKey = useCallback((code: string, down: boolean) => {
    if (down) heldKeys.current.add(code); else heldKeys.current.delete(code);
    window.dispatchEvent(new KeyboardEvent(down ? 'keydown' : 'keyup', { code, bubbles: true }));
  }, []);
  const releaseKeys = useCallback(() => {
    for (const code of heldKeys.current) sendKey(code, false);
  }, [sendKey]);
  const persist = useCallback((report = false) => {
    const current = engine.current;
    if (!current) return;
    try {
      const bytes = current.exportBattery();
      const state = batteryProgress(bytes);
      if (!state) return;
      setProgress(state);
      if (state.sequence !== lastSequence.current) {
        localStorage.setItem(storageKey, encodeSave(bytes));
        lastSequence.current = state.sequence;
      }
      if (report) setNotice('Saved on this device. Download a backup to move your game.');
      return bytes;
    } catch {
      if (report) setNotice('Device storage is unavailable. Use Save backup to keep your progress.');
    }
  }, [storageKey, batteryProgress]);
  useEffect(() => {
    if (!legacy && !romBytes) return;
    let disposed = false;
    let instance: Engine | null = null;
    const initialize = async () => {
      setPhase('loading');
      try {
        await loadRuntime();
        let rom = romBytes;
        if (legacy) {
          const response = await fetch('/game/sf-mini-monsters.gba');
          if (!response.ok) throw new Error('The cartridge could not be loaded.');
          rom = new Uint8Array(await response.arrayBuffer());
        }
        lastSequence.current = -1;
        instance = await window.sfMiniMonstersLoad!({ canvasEl: canvas.current, assets: { rom },
          jsUrl: '/emulator/mgba.js', wasmUrl: '/emulator/mgba.wasm', persist: null,
          onEvent: (event: {type: string; fps?: number}) => {
            if (event.type === 'frame' && Number.isFinite(event.fps) && canvas.current) {
              canvas.current.dataset.emulatorFps = event.fps!.toFixed(1);
            }
          },
          storageNamespace: storageKey, options: { system: 'gba', idleOptimization: 'ignore', volume: mutedRef.current ? 0 : 0.35, logLevel: 'error' } });
        if (disposed) { instance?.destroy(); return; }
        engine.current = instance;
        try {
          const saved = localStorage.getItem(storageKey);
          if (saved) {
            const bytes = decodeSave(saved); validateBattery(bytes);
            instance!.importBattery(bytes); setProgress(batteryProgress(bytes));
            setNotice(legacy ? 'Your game is ready to continue. Press A.' : 'Save restored. Press Start at the title screen, then choose Continue.');
          } else setNotice(legacy ? 'Press A to begin. Saves stay on this device.' : 'Press Start, then choose New Game. Save from the in-game menu before downloading a backup.');
        } catch { setNotice('The device save could not be restored. Import a valid backup or start a new delivery.'); }
        instance!.start(); setPhase('ready');
      } catch (error) {
        if (!disposed) { setPhase('error'); setNotice(error instanceof Error ? error.message : 'The game could not start.'); }
      }
    };
    void initialize();
    const interval = setInterval(() => persist(), 2500);
    const onHide = () => { releaseKeys(); persist(); };
    window.addEventListener('pagehide', onHide);
    window.addEventListener('blur', releaseKeys);
    return () => {
      disposed = true; clearInterval(interval); onHide();
      instance?.destroy(); engine.current = null;
      window.removeEventListener('pagehide', onHide); window.removeEventListener('blur', releaseKeys);
    };
  }, [storageKey, retry, persist, releaseKeys, legacy, romBytes, validateBattery, batteryProgress]);
  const loadRom = async (file?: File) => {
    if (!file) return;
    const wasRunning = !!engine.current;
    releaseKeys(); engine.current?.pause(); setPhase('verifying');
    try {
      if (file.size > 24 * 1024 * 1024) throw new Error('Select an Emerald .gba ROM or its ZIP archive.');
      await loadRuntime();
      const selected = new Uint8Array(await file.arrayBuffer());
      const {bytes} = await window.sfMiniMonstersExtract!(selected);
      const result = await patchLocalRom(bytes, edition);
      persist(); setRomBytes(result.rom); setNotice('Emerald verified and SF patch applied locally.');
      setPaused(false);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'The selected ROM could not be opened.');
      setPhase(wasRunning ? 'ready' : 'waiting');
      if (wasRunning && !paused) engine.current?.resume();
    }
    if (romInput.current) romInput.current.value = '';
  };
  const backup = () => {
    try {
      const bytes = engine.current!.exportBattery(); validateBattery(bytes);
      const url = URL.createObjectURL(new Blob([new Uint8Array(bytes)], { type: 'application/octet-stream' }));
      const link = document.createElement('a'); link.href = url; link.download = `${fileStem}.sav`;
      link.hidden = true; document.body.appendChild(link); link.click(); link.remove();
      setBackupUrl(url);
      persist(); setNotice('Backup prepared. Use Download save if your browser did not start the download.');
    } catch (error) { setNotice(legacy && error instanceof Error ? error.message : 'Save from the in-game menu first, then download a backup.'); }
  };
  const importSave = async (file?: File) => {
    if (!file || !engine.current) return;
    try {
      const bytes = new Uint8Array(await file.arrayBuffer()); validateBattery(bytes);
      const previous = persist();
      if (previous) localStorage.setItem(`${storageKey}:previous`, encodeSave(previous));
      engine.current.importBattery(bytes);
      setBackupUrl(null);
      localStorage.setItem(storageKey, encodeSave(bytes));
      lastSequence.current = -1; setProgress(batteryProgress(bytes));
      setNotice(legacy ? 'Backup restored. Press A to continue your delivery.' : 'Backup restored. Press Start at the title screen, then choose Continue.');
      if (paused) { engine.current.resume(); setPaused(false); }
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Could not import the save. Your progress was kept.'); }
    if (importInput.current) importInput.current.value = '';
  };
  const togglePause = () => {
    releaseKeys(); persist();
    if (paused) engine.current?.resume(); else engine.current?.pause();
    setPaused(!paused); canvas.current?.focus({ preventScroll: true });
  };
  const control = (label: string, code: string, className = '') => <button type="button" className={`game-key ${className}`}
    disabled={phase !== 'ready' || paused} aria-label={label} key={code}
    onClick={() => { sendKey(code, true); setTimeout(() => sendKey(code, false), 90); }}
    onPointerDown={event => { event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId); sendKey(code, true); }}
    onPointerUp={() => sendKey(code, false)} onPointerCancel={() => sendKey(code, false)}
    onLostPointerCapture={() => sendKey(code, false)}
    onKeyDown={event => { if (event.code === 'Space' || event.code === 'Enter') { event.preventDefault(); event.stopPropagation(); if (!event.repeat) sendKey(code, true); } }}
    onKeyUp={event => { if (event.code === 'Space' || event.code === 'Enter') { event.preventDefault(); event.stopPropagation(); sendKey(code, false); } }}>
    {label}</button>;
  return <main className={`game-site${world ? ' world-edition' : ''}`} onKeyDown={event => {
    if (world && (event.target as HTMLElement).closest('button,summary,a,input,select,textarea')) event.stopPropagation();
  }}>
    <header className="nav-edge">
      <span className="wordmark">SF MINI MONSTERS{world && <small>World preview</small>}</span>
      <a className="account-link" href={account ? signOutUrl : signInUrl} target="_top">
        {account ? 'Sign out' : 'Sign in with ChatGPT'}
      </a>
    </header>
    <div className="workbench">
      <section className="play-surface" aria-label="SF Mini Monsters game">
        <div className="screen-label"><span>{world ? 'SF WORLD PREVIEW' : 'THE FOG SIGNAL'}</span><span>{legacy ? progress ? MAPS[progress.map] : 'OUTER SUNSET' : world ? paused ? 'PAUSED' : phase === 'ready' ? 'READY TO PLAY' : 'GBA + WEB' : 'SUNSET PREVIEW'}</span></div>
        <div className="screen-stage" ref={screenStage}>
        <div className="game-screen" style={world ? { width: displayWidth, maxWidth: '100%' } : undefined}>
          <canvas ref={canvas} width={240} height={160} tabIndex={0} aria-label="GBA game screen. Arrow keys move, X confirms, Z goes back, Enter opens the menu." />
          {phase === 'waiting' && <div className="screen-overlay"><p>Bring your Emerald ROM.</p><button onClick={() => romInput.current?.click()}>Load .gba or ZIP</button><p>Patched here, on your device.</p></div>}
          {(phase === 'loading' || phase === 'verifying') && <div className="screen-overlay"><p>{phase === 'verifying' ? 'Checking and patching locally…' : 'Loading cartridge…'}</p></div>}
          {phase === 'error' && <div className="screen-overlay"><p>{notice}</p><button onClick={() => setRetry(retry + 1)}>Try again</button></div>}
          {paused && <div className="screen-overlay"><p>Paused</p><button onClick={togglePause}>Resume</button></div>}
        </div>
        </div>
        <div className={`input-strip${showGamepad ? ' touch-visible' : ''}`}>
          <div className="dpad" aria-label="Movement controls">
            {control('↑', 'ArrowUp', 'up')}{control('←', 'ArrowLeft', 'left')}
            {control('↓', 'ArrowDown', 'down')}{control('→', 'ArrowRight', 'right')}
          </div>
          <div className="utility-keys">{control('Select', 'ShiftRight')}{control('Start', 'Enter')}</div>
          <div className="action-keys">{control('B', 'KeyZ', 'key-b')}{control('A', 'KeyX', 'key-a')}</div>
        </div>
        <div className="player-actions">
          <button onClick={togglePause} disabled={phase !== 'ready'}>{paused ? 'Resume' : 'Pause'}</button>
          <button onClick={() => { const value = !muted; setMuted(value); mutedRef.current = value; engine.current?.config.write('volume', value ? 0 : 0.35); }} disabled={phase !== 'ready'}>{muted ? 'Sound on' : 'Mute'}</button>
          {world && <button onClick={() => setHelp(!help)} aria-expanded={help}>Controls</button>}
          {world && <button onClick={() => setCompactDisplay(!compactDisplay)} aria-pressed={compactDisplay}>2× display</button>}
          {world ? <details className="file-tools"><summary>Save &amp; files</summary><div>
            <p>Use Start → Save in the game first. World saves stay separate from the Sunset preview.</p>
            <button onClick={backup} disabled={phase !== 'ready'}>Download save</button>
            <button onClick={() => importInput.current?.click()} disabled={phase !== 'ready'}>Import world save</button>
            <button onClick={() => romInput.current?.click()} disabled={phase === 'verifying' || phase === 'loading'}>Choose another ROM</button>
            {romUrl && <a href={romUrl} download={`${fileStem}.gba`}>Download patched GBA</a>}
          </div></details> : <>
            <button onClick={backup} disabled={phase !== 'ready'}>Save backup</button>
            <button onClick={() => importInput.current?.click()} disabled={phase !== 'ready'}>Import save</button>
            <button onClick={() => setHelp(!help)} aria-expanded={help}>Controls</button>
            {!legacy && <button onClick={() => romInput.current?.click()} disabled={phase === 'verifying' || phase === 'loading'}>Load ROM</button>}
          </>}
          <input ref={importInput} type="file" accept=".sav" hidden onChange={event => void importSave(event.target.files?.[0])} />
          <input ref={romInput} type="file" accept=".gba,.zip" hidden onChange={event => void loadRom(event.target.files?.[0])} />
        </div>
        {world && <p className="keyboard-hints"><span><kbd>↑ ↓ ← →</kbd> Move</span><span><kbd>X</kbd> Talk</span><span><kbd>Z</kbd> Back</span><span><kbd>Enter</kbd> Menu</span></p>}
        <p className="save-notice" role="status">{notice}{backupUrl && <> <a href={backupUrl} download={`${fileStem}.sav`}>Download save</a></>}</p>
        {help && <div className="help-panel">
          {world && <button onClick={() => setShowGamepad(!showGamepad)} aria-pressed={showGamepad}>{showGamepad ? 'Hide' : 'Show'} on-screen gamepad</button>}
          <p><strong>Move:</strong> arrow keys or D-pad. <strong>Confirm / talk:</strong> X or A.</p>
          <p><strong>Back:</strong> Z or B. <strong>Menu:</strong> Enter or Start.</p>
          <p>{legacy ? 'In battle, use Up/Down to choose an action. Weaken wild monsters, then select Capture.' : world ? 'Hold B to run when available. Use Start → Save, then Save & files → Download save.' : 'Hold B to run when running is available. Save through Start → Save; then use Save backup.'}</p>
          {legacy && <p>Team/Storage: A puts a monster in the lead slot. Select releases a stored duplicate. Clinics heal for free.</p>}
          <p>The game saves progress on this device. Download a .sav backup before switching devices or clearing browser storage.</p>
        </div>}
      </section>
      {world ? <aside className="quest-sidebar world-sidebar">
        <div className="chapter-label">THE CITY IS YOUR ROUTE</div>
        <h1>Explore San Francisco.</h1>
        <p className="next-quest">Start in Dogpatch, meet the neighbors and follow the streets. Open SF Map from the in-game Start menu to find your next stop.</p>
        <ul className="world-facts"><li><strong>18</strong><span>destinations</span></li><li><strong>8</strong><span>gym sites</span></li><li><strong>2</strong><span>bay islands</span></li></ul>
        <div className="world-downloads">
          {romUrl && <a className="rom-link" href={romUrl} download={`${fileStem}.gba`}>Download GBA game</a>}
          <a className="source-link" href="/world-patch/sf-mini-monsters.bps" download>Download patch only</a>
          <a className="source-link" href="https://github.com/devk03/SF-Monsters" target="_blank" rel="noreferrer">Source &amp; contributions ↗</a>
        </div>
        <details className="preview-details"><summary>About this preview</summary>
          <p>Neighborhoods, local favors and service interiors are playable. Gym battles and contributor story missions are still being built. Gym rooms currently grant temporary access stamps; the loan creature is a development tool.</p>
          <p>Play as a guest. Signing in gives you a separate save slot on this device. Your ROM stays in your browser.</p>
          <a href="/">Sunset preview</a><a href="/prototype">Earlier courier prototype</a>
        </details>
      </aside> : <aside className="quest-sidebar">
        <div className="chapter-label">{world ? 'WORLD EXPLORATION PREVIEW' : legacy ? 'CHAPTER 01' : 'CHAPTER 01 PREVIEW'}</div>
        <h1>{world ? <>18 destinations.<br />One connected world.</> : <>A courier.<br />A missing parcel.<br />Very normal fog.</>}</h1>
        <p className="next-quest">{world ? 'Start in Dogpatch. Meet the neighbors, follow the streets and open SF Map from the Start menu. Gym rooms grant temporary access stamps so you can explore the whole route.' : legacy ? progress ? nextQuest(progress.flags) : 'Choose your companion, then find Roon’s prototype on Ocean Beach.' : 'Meet Karpathy by Judah, recover Roon’s sensor at Ocean Beach, then ride Muni to Cognition’s Build Challenge.'}</p>
        {legacy && <ol className="quest-list">{ROUTE.map(step => <li key={step.flag} className={progress && progress.flags & step.flag ? 'done' : ''}>
          <span aria-hidden="true">{progress && progress.flags & step.flag ? '✓' : '·'}</span>{step.label}
        </li>)}</ol>}
        {legacy && <div className="field-stats"><div><strong>{progress ? countCaught(progress.caught) : 0}<small>/12</small></strong><span>mini monsters</span></div>
          <div><strong>{progress?.flags && progress.flags & 64 ? '01' : '00'}</strong><span>gym badges</span></div></div>}
        <div className="delivery-note"><p>{world ? 'Compact streets · local favors · both islands' : 'Outer Sunset → Muni → South Park'}</p><p>{world ? 'San Francisco, plus the approved Angel Island League.' : 'Every stop is in San Francisco.'}</p></div>
        {(legacy || romUrl) && <a className="rom-link" href={legacy ? '/game/sf-mini-monsters.gba' : romUrl!} download={`${fileStem}.gba`}>Download GBA ROM</a>}
        {!legacy && <a className="rom-link" href={`${world ? '/world-patch' : '/patch'}/sf-mini-monsters.bps`} download>Download SF patch</a>}
        <a className="source-link" href="https://github.com/devk03/SF-Monsters" target="_blank" rel="noreferrer">Fork the game on GitHub</a>
        <p className="account-note">{account ? `Signed in as ${account.name}.` : 'Guest play is available. Sign in for a separate local save slot.'}</p>
        <p className="edition-note">{world ? 'Development preview: 18 destinations, 19 connectors, 13 small service interiors and 18 local activities. The loan creature and access stamps are temporary tools. Final gym battles, contributor missions, campaign balance and quality review remain unfinished. World saves are separate from v80 saves.' : legacy ? 'Earlier prototype: two neighborhoods, one gym, twelve monsters.' : 'Preview: the opening roster now has original art and cries—12 base creatures and six starter evolution stages. Explore Sunset, South Park and Cognition’s first gym. Pixel cleanup, cast, tiles, more music and the full 16-neighborhood campaign remain unfinished.'}</p>
        {!legacy && <a className="source-link" href={world ? '/' : '/world'}>{world ? 'Play the v80 Sunset preview' : 'Explore the new SF world preview'}</a>}
        {!legacy && <a className="source-link" href="/prototype">Play the earlier courier prototype</a>}
      </aside>}
    </div>
    <footer className="foot-line"><span>{world ? 'SF world draft · original residents · contributor gyms in progress' : 'SF fan project · real public personas · fictional adventure'}</span><a href="/emulator/NOTICE.txt">Emulator credits</a></footer>
  </main>;
}
