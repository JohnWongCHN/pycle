from click.testing import CliRunner
from pycle import pycle


def test_pycle():
    '''
    测试不调用子命令
    '''
    runner = CliRunner()
    result = runner.invoke(pycle.pycle, ['--host=172.16.200.170',
                                         '--port=1521',
                                         '--sid=xmcwdb',
                                         '--user=pycle',
                                         '--passwd=pycle'])
    print(result.output)
    assert result.exit_code == 0


def test_pycle_discovery():
    '''
    测试调用discovery
    '''
    runner = CliRunner()
    result = runner.invoke(pycle.pycle,
                           ['--host=172.16.200.170',
                            '--port=1521',
                            '--sid=xmcwdb',
                            '--user=pycle',
                            '--passwd=pycle',
                            'discovery',
                            '--discovery-type=tablespace_discovery'])
    print(result.output)
    assert result.exit_code == 0


def test_pycle_get_metric():
    '''
    测试调用get_metric
    '''
    runner = CliRunner()
    result = runner.invoke(pycle.pycle,
                           ['--host=172.16.200.170',
                            '--port=1521',
                            '--sid=xmcwdb',
                            '--user=pycle',
                            '--passwd=pycle',
                            'get-metric',
                            '--metric=count_of_active_users'])
    print(result.output)
    assert result.exit_code == 0
