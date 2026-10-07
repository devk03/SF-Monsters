import { load } from './mgba.sdk.js';
import { extractRom } from './mgba.zip.js';
window.sfMiniMonstersLoad = load;
window.sfMiniMonstersExtract = bytes => extractRom(bytes, ['.gba']);
