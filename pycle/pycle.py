#!/usr/bin/env python
# coding=UTF-8
'''
@Author: John Wong
@LastEditors: John Wong
@Description: 
@Date: 2019-03-29 09:18:05
@LastEditTime: 2019-08-28 14:25:24
'''

import click
import cx_Oracle

# sql 查询语句
sqls = {
    "dbversion": '''
                 select banner from v$version where rownum=1
                 ''',
    "dbsize": '''
              select sum(bytes) from dba_segments
              ''',
    "check_active": '''
                    select to_char(case when inst_cnt > 0 then 1 else 0 end,
                    'fm99999999999999990') retvalue from (select count(*) inst_cnt
                    from v$instance where status = 'open' and logins = 'allowed'
                    and database_status = 'active')
                    ''',
    "read_cache_hit_ratio": '''
                            select nvl(to_char((1 - (phy.value - lob.value - dir.value) /
                            ses.value) * 100, 'fm99999990.9999'), '0') retvalue
                            from   v$sysstat ses, v$sysstat lob,
                            v$sysstat dir, v$sysstat phy
                            where  ses.name = 'session logical reads'
                            and    dir.name = 'physical reads direct'
                            and    lob.name = 'physical reads direct (lob)'
                            and    phy.name = 'physical reads'
                            ''',
    "disk_sorts_ratio": '''
                        select nvl(to_char(d.value/(d.value + m.value)*100,
                        'fm99999990.9999'), '0') retvalue
                        from  v$sysstat m, v$sysstat d
                        where m.name = 'sorts (memory)'
                        and d.name = 'sorts (disk)'
                        ''',
    "count_of_active_users": '''
                             select to_char(count(*), 'fm99999999999999990') retvalue
                             from v$session where username is not null
                             and status='ACTIVE'
                             ''',
    "size_of_user_data": '''
                        select to_char(sum(  nvl(a.bytes - nvl(f.bytes, 0), 0)),
                        'fm99999999999999990') retvalue
                        from sys.dba_tablespaces d,
                        (select tablespace_name, sum(bytes) bytes from dba_data_files
                        group by tablespace_name) a,
                        (select tablespace_name, sum(bytes) bytes from
                        dba_free_space group by tablespace_name) f
                        where d.tablespace_name = a.tablespace_name(+) and
                        d.tablespace_name = f.tablespace_name(+)
                        and not (d.extent_management like 'local' and d.contents
                        like 'temporary')
                        ''',
    "dbfilesize": '''
                  select to_char(sum(bytes), 'fm99999999999999990') retvalue
                  from dba_data_files
                  ''',
    "dbuptime": '''
                select to_char((sysdate-startup_time)*86400,
                'fm99999999999999990') retvalue from v$instance
                ''',
    "usercommits": '''
                   select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                   v$sysstat where name = 'user commits'
                   ''',
    "userrollback": '''
                    select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                    v$sysstat where name = 'user rollbacks'
                    ''',
    "deadlocks": '''
                 select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                 v$sysstat where name = 'enqueue deadlocks'
                 ''',
    "redowrites": '''
                  select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                  v$sysstat where name = 'redo writes'
                  ''',
    "tablescans": '''
                  select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                  v$sysstat where name = 'table scans (long tables)'
                  ''',
    "tablerowscans": '''
                     select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                     v$sysstat where name = 'table scan rows gotten'
                     ''',
    "indexffs": '''
                select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                v$sysstat where name = 'index fast full scans (full)'
                ''',
    "hardparseratio": '''
                      select nvl(to_char(h.value/t.value*100,'fm99999990.9999'), '0')
                      retvalue from  v$sysstat h, v$sysstat t where h.name = 'parse count (hard)'
                      and t.name = 'parse count (total)'
                      ''',
    "netsent": '''
              select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
              v$sysstat where name = 'bytes sent via SQL*Net to client'
              ''',
    "netrecv": '''
               select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
               v$sysstat where name = 'bytes received via SQL*Net from client'
               ''',
    "netroundtrips": '''
                     select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                     v$sysstat where name = 'SQL*Net roundtrips to/from client'
                     ''',
    "currentloggons": '''
                      select nvl(to_char(value, 'fm99999999999999990'), '0') retvalue from
                      v$sysstat where name = 'logons current'
                      ''',
    "lastarch": '''
                select to_char(max(sequence#), 'fm99999999999999990')
                retvalue from v$log where archived = 'YES'
                ''',
    "lastapplyarch": '''
                     select to_char(max(lh.sequence#), 'fm99999999999999990')
                     retvalue from v$log_history lh, v$archived_log al
                     where lh.sequence# = al.sequence# and applied='YES'
                     ''',
    "freebuffwaits": '''
                     select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                     from v$system_event se, v$event_name en
                     where se.event(+) = en.name and en.name = 'free buffer waits'
                     ''',
    "busybuffwaits": '''
                     select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                     from v$system_event se, v$event_name en where se.event(+) =
                     en.name and en.name = 'buffer busy waits'
                     ''',
    "logswitcompletion": '''
                         select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                         from v$system_event se, v$event_name en where se.event(+)
                         = en.name and en.name = 'log file switch completion'
                         ''',
    "logfilesync": '''
                   select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                   from v$system_event se, v$event_name en
                   where se.event(+) = en.name and en.name = 'log file sync'
                   ''',
    "logparallelwrite": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'log file parallel write'
                        ''',
    "dbseqreadwait": '''
                     select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                     from v$system_event se, v$event_name en where se.event(+)
                     = en.name and en.name = 'db file sequential read'
                     ''',
    "dbscatteredread": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'db file scattered read'
                        ''',
    "dbsinglewrite": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'db file single write'
                     ''',
    "dbparallelwrite": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'db file parallel write'
                        ''',
    "directpathread": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'direct path read'
                        ''',
    "directpathwrite": '''
                        select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                        from v$system_event se, v$event_name en where se.event(+)
                        = en.name and en.name = 'direct path write'
                       ''',
    "latchfree": '''
                 select nvl(to_char(time_waited, 'fm99999999999999990'), '0') retvalue
                 from v$system_event se, v$event_name en where se.event(+)
                 = en.name and en.name = 'latch free'
                 ''',
    "tablespace": '''
                    select  tablespace_name,
                    100-(trunc((max_free_mb/max_size_mb) * 100)) as used
                    from ( select a.tablespace_name,b.size_mb,a.free_mb,b.max_size_mb,a.free_mb + (b.max_size_mb - b.size_mb) as max_free_mb
                    from   (select tablespace_name,trunc(sum(bytes)/1024/1024) as free_mb from dba_free_space group by tablespace_name) a,
                    (select tablespace_name,trunc(sum(bytes)/1024/1024) as size_mb,trunc(sum(greatest(bytes,maxbytes))/1024/1024) as max_size_mb
                    from   dba_data_files group by tablespace_name) b where  a.tablespace_name = b.tablespace_name
                    ) where tablespace_name='{0}' order by 1
                  ''',
    "tablespaceinuse": '''
                        select df.tablespace_name "tablespace", (df.totalspace -
                        tu.totalusedspace) "freemb" from (select tablespace_name,
                        sum(bytes) totalspace from dba_data_files group by tablespace_name)
                        df ,(select sum(bytes) totalusedspace,tablespace_name from dba_segments
                        group by tablespace_name) tu where tu.tablespace_name =
                        df.tablespace_name and df.tablespace_name = '{0}'
                        ''',
}

check_item = tuple(sqls.keys())


# @click.group(chain=True)
@click.group()
def main():
    '''
    A CLI utility to check some database \n
    example: \n
    pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'
    '''
    pass

# @click.group()
@main.command(help=u'查询Oracle')
@click.option('-h', '--host', default='127.0.0.1', required=True, help=u'数据库IP地址')
@click.option('-p', '--port', default='1521', required=True, help=u'数据库监听端口')
@click.option('-s', '--sid', default='orcl', required=True, help=u'数据库实例SID')
@click.option('-u', '--user', default='PYCLE', required=True, help=u'数据库用户名')
@click.option('-P', '--passwd', default='pycle', required=True, help=u'用户密码')
@click.option('-c', '--check', default='dbversion', required=False, type=click.Choice(check_item), help='查询目标')
@click.option('-C', '--checkparam', default='', required=False, multiple=True, help=u'查询参数')
def chk_oracle(host, port, sid, user, passwd, **kwargs):
    '''
    查询Oracle
    '''
    # get check type, default is dbversion
    check = kwargs.get('check')
    # get sql statement
    sql = sqls.get(check).strip()
    # conn to oracle
    dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
    try:
        connection = cx_Oracle.connect(
            user=user, password=passwd, dsn=dsn, encoding='utf-8')
        cursor = connection.cursor()
        cursor.execute(sql)
        ret = cursor.fetchall()
        for i in ret:
            # 如果返回空值，那么额外处理
            click.echo(i[0])
        connection.close()
    except Exception as e:
        click.echo(str(e))


# @main.command(help=u'查询Mysql --待开发')
# def chk_mysql():
#     pass


# @main.command(help=u'查询mongo --待开发')
# def chk_mongo():
#     pass


if __name__ == "__main__":
    main()
