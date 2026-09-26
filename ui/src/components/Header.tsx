import { Bars3BottomLeftIcon, CircleStackIcon, CloudIcon, CommandLineIcon, FolderIcon } from '@heroicons/react/24/outline';
import { useSelector } from 'react-redux';
import { selectConfig, selectInfo, selectReadonly } from '~/app/meta/metaSlice';
import { useSession } from '~/data/hooks/session';
import { StorageType } from '~/types/Meta';
import Notifications from './header/Notifications';
import UserProfile from './header/UserProfile';

type HeaderProps = {
  setSidebarOpen: (sidebarOpen: boolean) => void;
};

export default function Header(props: HeaderProps) {
  const { setSidebarOpen } = props;

  const info = useSelector(selectInfo);
  const readOnly = useSelector(selectReadonly);
  const config = useSelector(selectConfig);

  const { session } = useSession();

  const StorageIcon = (() => {
    switch (config?.storage?.type) {
      case StorageType.DATABASE:
        return CircleStackIcon;
      case StorageType.LOCAL:
        return FolderIcon;
      case StorageType.GIT:
        return CommandLineIcon;
      case StorageType.OBJECT:
        return CloudIcon;
      default:
        return CircleStackIcon;
    }
  })();

  return (
    <div className="bg-violet-400 sticky top-0 z-10 flex h-16 flex-shrink-0">
      <button
        type="button"
        className="without-ring text-white px-4 md:hidden"
        onClick={() => setSidebarOpen(true)}
      >
        <span className="sr-only">Open sidebar</span>
        <Bars3BottomLeftIcon className="h-6 w-6" aria-hidden="true" />
      </button>

      <div className="flex flex-1 justify-between px-4">
        <div className="flex flex-1" />
        <div className="ml-4 flex items-center space-x-1.5 md:ml-6">
          {/* read-only mode */}
          {readOnly && (
            <span className="nightwind-prevent bg-violet-200 inline-flex items-center gap-x-1.5 rounded-full px-3 py-1 text-xs font-medium text-violet-950">
              <StorageIcon className="h-4 w-4" aria-hidden="true" />
              Read-Only
            </span>
          )}
          {/* notifications */}
          {info && info.updateAvailable && <Notifications info={info} />}

          {/* user profile */}
          {session && session.self && (
            <UserProfile
              name={session.self.metadata['io.flipt.auth.oidc.name']}
              imgURL={session.self.metadata['io.flipt.auth.oidc.picture']}
            />
          )}
        </div>
      </div>
    </div>
  );
}
