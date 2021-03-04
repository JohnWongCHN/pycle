#!/usr/local/bin/python3

import click
import cx_Oracle
import json


@click.group(invoke_without_command=True)
@click.option('-h', '--host', default='127.0.0.1', required=True, help=u'IP地址')
@click.option('-p', '--port', default='1521', required=True, help=u'监听端口')
@click.option('-s', '--service-name', default='orcl', required=True, help=u'服务名')
@click.option('-u', '--user', default='PYCLE', required=True, help=u'用户名')
@click.option('-P', '--passwd', default='pycle', required=True, help=u'密码')
@click.pass_context
def pycle(ctx, host, port, service_name, user, passwd):
    '''
    A CLI utility to check some database \n
    example: \n
    pycle -h 172.16.2.91 -p 1521 -s ywptdata1 -u pycle -P pycle get-metric -m asm_size -v DATA
    '''

    # make dsn and connect to Oracle instance
    dsn = cx_Oracle.makedsn(host=host, port=port, service_name=service_name)
    conn_parameter = {'username': user, 'password': passwd, 'dsn': dsn}
    try:
        conn = cx_Oracle.connect(
            user=conn_parameter.get('username'),
            password=conn_parameter.get('password'),
            dsn=conn_parameter.get('dsn'),
            encoding='utf-8'
        )
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    else:
        if ctx.invoked_subcommand is None:
            cursor = conn.cursor()
            try:
                sql = """
                    select instance_name, host_name, version, status
                    from v$instance
                """
                sql = sql.strip()
                cursor.execute(sql)
            except cx_Oracle.DatabaseError as exc:
                error, = exc.args
                click.echo("Message: {}.".format(error.message))
            rows = cursor.fetchall()
            for row in rows:
                click.echo(row)
            
            # 关闭 connection
            conn.close()
        else:
            ctx.obj = conn

@pycle.command()
@click.pass_obj
def get_archivelog_stats(ctx):
    """
    获取归档信息
    """
    sql = """
        SELECT
        d.dest_name, DECODE (d.status, 'VALID',3, 'DEFERRED', 2, 'ERROR', 1, 0) AS status,
        d.log_sequence,
        d.error
        FROM v$archive_dest d , v$database db
        WHERE d.status != 'INACTIVE' AND db.log_mode = 'ARCHIVELOG'
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.option('-l', '--session-lock-max-time', default=600, required=True, help=u'Oracle session lock max time')
@click.pass_obj
def get_system_metrics_1(ctx, session_lock_max_time):
    """
    获取系统指标 1
    """
    sql = """
        SELECT 'SYS::' || METRIC_NAME AS METRIC, ROUND(VALUE,3) AS VALUE
        FROM V$SYSMETRIC WHERE GROUP_ID = 2
        UNION
        SELECT 'SYSPARAM::' || INITCAP(NAME), to_number(VALUE)
        FROM V$SYSTEM_PARAMETER WHERE NAME IN ('sessions', 'processes', 'db_files')
        UNION
        SELECT 'SESSION::Long time locked' ,count(*) FROM V$SESSION s WHERE s.BLOCKING_SESSION IS NOT NULL AND s.BLOCKING_SESSION_STATUS='VALID' AND s.SECONDS_IN_WAIT > :session_lock_max_time
        UNION
        SELECT 'SESSION::Lock rate' ,(cnt_block / cnt_all)* 100 pct
        FROM ( SELECT COUNT(*) cnt_block FROM v$session WHERE blocking_session IS NOT NULL), ( SELECT COUNT(*) cnt_all FROM v$session)
        UNION
        SELECT 'SESSION::Total', COUNT(*) FROM V$SESSION
        UNION
        SELECT 'SESSION::' || INITCAP(STATUS)|| ' ' || INITCAP(TYPE), COUNT(*) FROM V$SESSION GROUP BY STATUS, TYPE
        UNION
        SELECT 'SESSION::Concurrency rate', NVL(ROUND(SUM(duty_act.cnt*100 / num_cores.val)), 0)
        FROM
        ( SELECT DECODE(session_state, 'ON CPU', 'CPU', wait_class) wait_class, ROUND(COUNT(*)/(60 * 15), 1) cnt
        FROM v$active_session_history sh
        WHERE sh.sample_time >= SYSDATE - 15 / 1440 AND DECODE(session_state, 'ON CPU', 'CPU', wait_class) IN('Concurrency')
        GROUP BY DECODE(session_state, 'ON CPU', 'CPU', wait_class)) duty_act,
        ( SELECT SUM(value) val FROM v$osstat WHERE stat_name = 'NUM_CPU_CORES') num_cores
        UNION
        SELECT 'PGA::' || INITCAP(NAME), VALUE FROM V$PGASTAT
        UNION
        SELECT 'PROC::Procnum', COUNT(*) FROM v$process
        UNION
        SELECT 'DATAFILE::Count', COUNT(*) FROM v$datafile
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        # use bind variable
        cursor.execute(sql, [session_lock_max_time,])
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def get_asm_stats(ctx):
    """
    获取 ASM 磁盘信息
    """
    sql = """
        SELECT
        name AS dg_name,
        ROUND(total_mb / DECODE(TYPE, 'NORMAL', 2, 'HIGH', 3, 'EXTERN', 1)*1024*1024) AS size_byte,
        ROUND(usable_file_mb*1024*1024 ) AS free_size_byte,
        ROUND(100-(usable_file_mb /(total_mb / DECODE(TYPE, 'NORMAL', 2, 'HIGH', 3, 'EXTERN', 1)))* 100, 2) AS used_percent
        FROM v$asm_diskgroup
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def get_tablespace_stats(ctx):
    """
    获取表空间信息
    """
    sql = """
        SELECT NVL (b.tablespace_name, NVL (a.tablespace_name, 'UNKNOWN')) as tablespace,
        dt.contents as type,
        dt.status as status,
        round(bytes_alloc - NVL (bytes_free, 0), 2) as used_bytes,
        round(NVL (bytes_free, 0), 2) as free_bytes,
        round(bytes_alloc, 2) as allocated_bytes,
        round(( (bytes_alloc - NVL (bytes_free, 0)) / bytes_alloc) * 100, 2) as used_pct_allocated,
        round(bytes_max, 2) as max_bytes,
        CASE
            WHEN bytes_max > 0
            THEN round(( (bytes_alloc - NVL (bytes_free, 0)) / bytes_max) * 100, 2)
        END as used_pct_max
        FROM
        (SELECT SUM (bytes) bytes_free,
            tablespace_name
        FROM sys.dba_free_space
        GROUP BY tablespace_name
        UNION
        SELECT SUM (free_space) bytes_free,
            tablespace_name
        FROM sys.dba_temp_free_space
        GROUP BY tablespace_name
        ) a,
        (SELECT SUM (bytes) bytes_alloc,
            SUM (maxbytes) bytes_max,
            tablespace_name,
            COUNT (*) data_files
        FROM sys.dba_data_files
        GROUP BY tablespace_name
        UNION
        SELECT SUM (bytes) bytes_alloc,
            SUM (maxbytes) bytes_max,
            tablespace_name,
            COUNT (*) data_files
        FROM sys.dba_temp_files
        GROUP BY tablespace_name
        ) b,
        (SELECT tablespace_name,
            decode(status,'ONLINE',1,'OFFLINE',2,'READ ONLY',3,0) as status,
            contents
        FROM dba_tablespaces
        ) dt
        WHERE a.tablespace_name(+) = b.tablespace_name
        and b.tablespace_name(+) = dt.tablespace_name
        AND ( b.tablespace_name IS NULL
        OR INSTR (LOWER (b.tablespace_name), LOWER (b.tablespace_name)) > 0)
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.option('-s', '--schema-name', default='pycle', required=True, help=u'Oracle schema name')
@click.pass_obj
def get_system_metrics_2(ctx, schema_name):
    """
    获取系统指标 2
    """
    sql = """
        SELECT 'SGA::' || INITCAP(pool) AS METRIC , SUM(bytes) AS VALUE FROM V$SGASTAT
        WHERE pool IN ( 'java pool', 'large pool' ) GROUP BY pool
        UNION
        SELECT 'SGA::Shared Pool', SUM(bytes) FROM V$SGASTAT
        WHERE pool = 'shared pool' AND name NOT IN ('library cache', 'dictionary cache', 'free memory', 'sql area')
        UNION
        SELECT 'SGA::' || INITCAP(name), bytes FROM V$SGASTAT
        WHERE pool IS NULL AND name IN ('log_buffer', 'fixed_sga')
        UNION
        SELECT 'SGA::Buffer_Cache', SUM(bytes) FROM V$SGASTAT
        WHERE pool IS NULL AND name IN ('buffer_cache', 'db_block_buffers')
        UNION
        SELECT 'REDO::Available', count(*) from v$log t where t.status in ('INACTIVE', 'UNUSED')
        UNION
        SELECT 'USER::Expire password', ROUND(DECODE(SIGN(NVL(u.expiry_date, SYSDATE + 999) - SYSDATE),-1, 0, NVL(u.expiry_date, SYSDATE + 999) - SYSDATE)) exp_passwd_days_before
        FROM dba_users u WHERE username = UPPER(:schema)
        UNION
        SELECT 'FRA::Space Limit', space_limit FROM V$RECOVERY_FILE_DEST
        UNION
        SELECT 'FRA::Space Used', space_used FROM V$RECOVERY_FILE_DEST
        UNION
        SELECT 'FRA::Space Reclaimable', space_reclaimable FROM V$RECOVERY_FILE_DEST
        UNION
        SELECT 'FRA::Number Of Files', number_of_files FROM V$RECOVERY_FILE_DEST
        UNION
        SELECT 'FRA::Usable Pct', DECODE(space_limit, 0, 0,(100-(100 *(space_used-space_reclaimable)/ space_limit))) AS VALUE FROM V$RECOVERY_FILE_DEST
        UNION
        SELECT 'FRA::Restore Point', COUNT(*) FROM V$RESTORE_POINT
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql, [schema_name,])
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def get_cdb_info(ctx):
    """
    获取容器 DB 信息
    """
    sql = """
        SELECT name as DBNAME,
        DECODE(open_mode, 'MOUNTED', 1, 'READ ONLY', 2, 'READ WRITE', 3, 'READ ONLY WITH APPLY', 4, 'MIGRATE', 5, 0) AS open_mode,
        DECODE(database_role, 'SNAPSHOT STANDBY', 1, 'LOGICAL STANDBY', 2, 'PHYSICAL STANDBY', 3, 'PRIMARY', 4, 'FAR SYNC', 5, 0) AS ROLE,
        DECODE(force_logging, 'YES',1,'NO',0,0) AS force_logging,
        DECODE(log_mode, 'MANUAL',2 ,'ARCHIVELOG',1,'NOARCHIVELOG',0,0) AS log_mode
        FROM v$database
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def get_pdb_info(ctx):
    """
    获取可插拔 DB 信息
    """
    sql = """
        SELECT
        name as DBNAME,
        DECODE(open_mode, 'MOUNTED', 1, 'READ ONLY', 2, 'READ WRITE', 3, 'READ ONLY WITH APPLY', 4, 'MIGRATE', 5, 0) AS open_mode
        FROM v$pdbs
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def get_instance_stats(ctx):
    """
    获取实例信息
    """
    sql = """
        SELECT
        INSTANCE_NAME,
        HOST_NAME,
        VERSION AS VERSION,
        floor((SYSDATE - startup_time)*60*60*24) AS UPTIME,
        decode(status,'STARTED',1,'MOUNTED',2,'OPEN',3,'OPEN MIGRATE',4, 0) AS STATUS,
        decode(archiver,'STOPPED',1,'STARTED',2,'FAILED',3, 0) AS  ARCHIVER,
        decode(instance_role,'PRIMARY_INSTANCE',1,'SECONDARY_INSTANCE',2, 0) AS  INSTANCE_ROLE
        FROM v$instance
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def discovery_archivelog(ctx):
    """
    discovery archivelog info
    """
    sql = """
        SELECT d.dest_name as "{#DEST_NAME}"
        FROM v$archive_dest d , v$database db WHERE d.status != 'INACTIVE' AND db.log_mode = 'ARCHIVELOG'
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def discovery_asm(ctx):
    """
    discovery asm
    """
    sql = """
        SELECT name AS "{#DG_NAME}" FROM v$asm_diskgroup
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def discovery_database(ctx):
    """
    discovery database
    """
    sql = """
        SELECT name as "{#DBNAME}", 'DB' AS "{#TYPE}"  FROM V$DATABASE
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def discovery_pdb(ctx):
    """
    discovery pdb
    """
    sql = """
        SELECT name as "{#DBNAME}" FROM V$PDBS
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

@pycle.command()
@click.pass_obj
def discovery_tablespace(ctx):
    """
    discovery tablespace
    """
    sql = """
        SELECT
        tablespace_name AS "{#TABLESPACE}",
        contents AS "{#CONTENTS}"
        FROM DBA_TABLESPACES
    """
    sql = sql.strip()
    try:
        conn = ctx
        cursor = conn.cursor()
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        click.echo("Message: {}.".format(error.message))
    except Exception as exc:
        pass
    else:
        # Changing Query Results with Rowfactories
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        rows = cursor.fetchall()
        ret = []
        for row in rows:
            ret.append(row)
        click.echo(json.dumps(ret))

        # 关闭 connection
        conn.close()

if __name__ == "__main__":
    pycle()
