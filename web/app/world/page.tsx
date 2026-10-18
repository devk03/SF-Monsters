import GamePlayer from '../player';
import { chatGPTSignInPath, chatGPTSignOutPath, getChatGPTUser } from '../chatgpt-auth';
export const dynamic = 'force-dynamic';
export const metadata = { title: 'SF Mini Monsters — World Preview' };
export default async function World() {
  const user = await getChatGPTUser();
  return <GamePlayer variant="world" account={user ? { id: user.userId, name: user.displayName } : null}
    signInUrl={chatGPTSignInPath('/world')} signOutUrl={chatGPTSignOutPath('/world')} />;
}
