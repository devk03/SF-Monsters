import GamePlayer from '../player';
import {chatGPTSignInPath, chatGPTSignOutPath, getChatGPTUser} from '../chatgpt-auth';
export const dynamic = 'force-dynamic';
export default async function Prototype() {
  const user = await getChatGPTUser();
  return <GamePlayer variant="prototype" account={user ? {id: user.userId, name: user.displayName} : null}
    signInUrl={chatGPTSignInPath('/prototype')} signOutUrl={chatGPTSignOutPath('/prototype')} />;
}
