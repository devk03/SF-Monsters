// Separate world entry; the Sunset loader and its globals remain unchanged.
import { load } from './world.sdk.js';
import { extractRom } from './mgba.zip.js';
window.sfWorldMonstersLoad = load;
window.sfWorldMonstersExtract = bytes => extractRom(bytes, ['.gba']);
