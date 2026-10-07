import GamePlayer from './player';
import { chatGPTSignInPath, chatGPTSignOutPath, getChatGPTUser } from './chatgpt-auth';
export const dynamic = 'force-dynamic';
export default async function Home() {
  const user = await getChatGPTUser();
  return <GamePlayer account={user ? { id: user.userId, name: user.displayName } : null}
    signInUrl={chatGPTSignInPath('/play')} signOutUrl={chatGPTSignOutPath('/')} />;
}
