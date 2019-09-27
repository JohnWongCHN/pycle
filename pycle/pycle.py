import click
import cx_Oracle
import pandas as pd
from pkg_resources import resource_stream
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# 读取包中配置文件并转成dict
sqls = load(resource_stream('pycle', 'config/sql.yml'), Loader=Loader)


@click.group(invoke_without_command=True)
@click.option('-h', '--host', default='127.0.0.1', required=True, help=u'IP地址')
@click.option('-p', '--port', default='1521', required=True, help=u'监听端口')
@click.option('-s', '--sid', default='orcl', required=True, help=u'实例SID')
@click.option('-u', '--user', default='PYCLE', required=True, help=u'用户名')
@click.option('-P', '--passwd', default='pycle', required=True, help=u'密码')
@click.pass_context
def pycle(ctx, host, port, sid, user, passwd):
    '''
    A CLI utility to check some database \n
    example: \n
    pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'
    '''
    # make dsn and connect to Oracle instance
    dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
    conn_parameter = {'username': user, 'password': passwd, 'dsn': dsn}
    try:
        if ctx.invoked_subcommand is None:
            with cx_Oracle.connect(user=conn_parameter.get('username'),
                                   password=conn_parameter.get('password'),
                                   dsn=conn_parameter.get('dsn'),
                                   encoding='utf-8') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    'select instance_name, host_name, version, status \
                     from v$instance')
                rows = cursor.fetchall()
                click.echo('当前数据库实例信息如下:\n')
                for row in rows:
                    click.echo(row)
        else:
            ctx.obj = conn_parameter
    except Exception as e:
        click.echo(str(e))


@pycle.command()
@click.option('-d', '--discovery-type', required=True, help='discovery类型')
@click.pass_obj
def discovery(conn_parameter, discovery_type):
    '''
    获得多行多列值，返回json格式，供zabbix进行low level discovery采集
    '''
    if discovery_type in sqls:
        sql = sqls.get(discovery_type)
        try:
            with cx_Oracle.connect(user=conn_parameter.get('username'),
                                   password=conn_parameter.get('password'),
                                   dsn=conn_parameter.get('dsn'),
                                   encoding='utf-8') as connection:
                ret_json = pd.read_sql(sql=sql, con=connection).to_json()
                click.echo(ret_json)
        except Exception as e:
            click.echo(str(e))
    else:
        click.echo('配置字典中不存在该参数')


@pycle.command()
@click.option('-m', '--metric', required=True, help='查询指标')
@click.option('-v', '--variable', help='可选参数，用于带条件的sql语句')
@click.pass_obj
def get_metric(conn_parameter, metric, variable):
    '''
    获取指标，返回单个值，供zabbix采集监控
    '''
    if metric in sqls:
        sql = sqls.get(metric).format(variable)
        try:
            with cx_Oracle.connect(user=conn_parameter.get('username'),
                                   password=conn_parameter.get('password'),
                                   dsn=conn_parameter.get('dsn'),
                                   encoding='utf-8') as connection:
                cursor = connection.cursor()
                ret_vale = cursor.execute(sql).fetchall()
                for row in ret_vale:
                    click.echo(row[0])
        except Exception as e:
            click.echo(str(e))
    else:
        click.echo('配置字典中不存在该参数')

if __name__ == "__main__":
    pycle()
