import GamePlayer from '../player';
import { chatGPTSignInPath, chatGPTSignOutPath, requireChatGPTUser } from '../chatgpt-auth';
export const dynamic = 'force-dynamic';
export default async function Play() {
  const user = await requireChatGPTUser('/play');
  return <GamePlayer account={{ id: user.userId, name: user.displayName }}
    signInUrl={chatGPTSignInPath('/play')} signOutUrl={chatGPTSignOutPath('/')} />;
}
