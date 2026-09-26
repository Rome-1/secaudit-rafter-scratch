from unittest.mock import patch
from scripts.monitoring.utils import OlAsyncIOScheduler, limit_server

with patch('os.environ.get', return_value='ol-web0.us.archive.org'):
    scheduler = OlAsyncIOScheduler()
    @limit_server(['ol-web0', 'ol-covers0'], scheduler)
    @scheduler.scheduled_job('interval', seconds=60)
    def sample():
        pass
    print('job exists?', scheduler.get_job('sample') is not None)

with patch('os.environ.get', return_value='ol-covers0'):
    scheduler = OlAsyncIOScheduler()
    @limit_server(['ol-web0*'], scheduler)
    @scheduler.scheduled_job('interval', seconds=60)
    def other():
        pass
    print('other exists?', scheduler.get_job('other') is not None)
