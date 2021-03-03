# Python CLI Tool to Monitor Oracle Database

[TOC]

I name it **Pycle**, which means `Python` + `Oracle`. It's inspired by another open source python scripts - Pyora, and it's website is <https://github.com/bicofino/Pyora>

Pyora is good, but with some disadvantes, it does not support Python 3. So i try to use `Click`, `cx_Oracle` rewirte it, make it more compatible with Python 2 & Python 3.

Which `Click` is another great package to build CLI utility, official site: <https://click.palletsprojects.com/en/7.x/>

> Click is a Python package for creating beautiful command line interfaces in a composable way with as little code as necessary. It’s the “Command Line Interface Creation Kit”. It’s highly configurable but comes with sensible defaults out of the box.
>
> It aims to make the process of writing command line tools quick and fun while also preventing any frustration caused by the inability to implement an intended CLI API.

Which cx_Oracle is developed by Oracle, official site: <https://cx-oracle.readthedocs.io/en/latest/>

> **cx_Oracle** is a module that enables access to Oracle Database and conforms to the Python database API specification. This module is currently tested against Oracle Client 11.2, 12.1, 12.2 and 18.3 and Python 2.7, 3.5, 3.6 and 3.7.

## How to install pycle

For easy to use, i built it as a python wheel package to resolve package dependency.

So you can download the wheel package and run bellow command to install on your machine

```shell
# which Pycle-0.0.2-py3-none-any.whl is on your local file system
$ pip install Pycle-0.0.2-py3-none-any.whl

# run test
$ pycle --help
Usage: pycle [OPTIONS] COMMAND [ARGS]...

  A CLI utility to check some database

  example:

  pycle -h 172.16.2.91 -p 1521 -s ywptdata1 -u pycle -P pycle get-metric -m asm_size -v DATA

Options:
  -h, --host TEXT    IP地址  [required]
  -p, --port TEXT    监听端口  [required]
  -s, --sid TEXT     实例SID  [required]
  -u, --user TEXT    用户名  [required]
  -P, --passwd TEXT  密码  [required]
  --help             Show this message and exit.

Commands:
  discovery   获得多行值，返回json格式，供zabbix进行low level discovery采集
  get-metric  获取指标，返回单个值，供zabbix采集监控
```

Or you can just download `pycle.py` scripts, but in this way you need to resolve dependency package by yourself

run bellow command

```shell
# install dependency package
$ pip install click
$ pip install cx_Oracle

# run test
$ python pycle.py --help
Usage: pycle [OPTIONS] COMMAND [ARGS]...

  A CLI utility to check some database

  example:

  pycle -h 172.16.2.91 -p 1521 -s ywptdata1 -u pycle -P pycle get-metric -m asm_size -v DATA

Options:
  -h, --host TEXT    IP地址  [required]
  -p, --port TEXT    监听端口  [required]
  -s, --sid TEXT     实例SID  [required]
  -u, --user TEXT    用户名  [required]
  -P, --passwd TEXT  密码  [required]
  --help             Show this message and exit.

Commands:
  discovery   获得多行值，返回json格式，供zabbix进行low level discovery采集
  get-metric  获取指标，返回单个值，供zabbix采集监控
```

## How to Use

There are two way to use this utility, run `pycle` command or run `pycle.py` scripts directly. Before use to check Oracle database, you need create a user `pycle`, bellow is creation script

```sql
CREATE USER PYCLE IDENTIFIED BY PYCLE;
GRANT CONNECT, CREATE SESSION TO "PYCLE";
GRANT SELECT ON V_$INSTANCE TO "PYCLE";
GRANT SELECT ON V_$SESSION TO "PYCLE";
GRANT SELECT ON V_$SYSSTAT TO "PYCLE";
GRANT SELECT ON V_$SYSTEM_EVENT TO "PYCLE";
GRANT SELECT ON V_$ASM_DISKGROUP TO "PYCLE";
GRANT SELECT ON V_$SYS_TIME_MODEL TO "PYCLE";
GRANT SELECT ON V_$PARAMETER TO "PYCLE";
GRANT SELECT ON V_$LATCH TO "PYCLE";
GRANT SELECT ON V_$LATCH_CHILDREN TO "PYCLE";
GRANT SELECT ON V_$SGASTAT TO "PYCLE";
GRANT SELECT ON V_$RESOURCE_LIMIT TO "PYCLE";
GRANT SELECT ON V_$DATAFILE TO "PYCLE";
GRANT SELECT ON V_$PX_SESSION TO "PYCLE";
GRANT SELECT ON V_$DISPATCHER TO "PYCLE";
GRANT SELECT ON V_$SHARED_SERVER TO "PYCLE";
GRANT SELECT ON V_$TABLESPACE TO "PYCLE";
GRANT SELECT ON V_$ARCHIVED_LOG TO "PYCLE";
GRANT SELECT ON V_$RMAN_STATUS TO "PYCLE";
GRANT SELECT ON V_$MEMORY_DYNAMIC_COMPONENTS TO "PYCLE";
GRANT SELECT ON V_$LOG TO "PYCLE";
GRANT SELECT ON V_$EVENT_NAME TO "PYCLE";
GRANT SELECT ON V_$ARCHIVE_DEST TO "PYCLE";
GRANT SELECT ON V_$LOG_HISTORY TO "PYCLE";
GRANT SELECT ON V_$DATABASE TO "PYCLE";
GRANT SELECT ON V_$OSSTAT TO "PYCLE";
GRANT SELECT ON V_$PROCESS TO "PYCLE";
GRANT SELECT ON V_$TEMP_SPACE_HEADER TO "PYCLE";
GRANT SELECT ON V_$TEMP_EXTENT_POOL  TO "PYCLE";
GRANT SELECT ON V_$ASM_DISK TO "PYCLE";
GRANT SELECT ON V_$ASM_FILE TO "PYCLE";
GRANT SELECT ON V_$RECOVERY_FILE_DEST TO "PYCLE";
GRANT SELECT ON V_$FLASH_RECOVERY_AREA_USAGE TO "PYCLE";
GRANT SELECT ON V_$SESSION TO "PYCLE";
GRANT SELECT ON V_$TRANSACTION TO "PYCLE";
GRANT SELECT ON V_$ROLLNAME TO "PYCLE";
GRANT SELECT ON V_$ROLLSTAT TO "PYCLE";
GRANT SELECT ON V_$SORT_USAGE TO "PYCLE";
GRANT SELECT ON V_$DB_OBJECT_CACHE TO "PYCLE";
GRANT SELECT ON V_$SQLAREA TO "PYCLE";
GRANT SELECT ON V_$SESSTAT TO "PYCLE";
GRANT SELECT ON V_$STATNAME TO "PYCLE";
GRANT SELECT ON V_$STANDBY_LOG TO "PYCLE";
GRANT SELECT ON V_$LOGFILE TO "PYCLE";
GRANT SELECT ON V_$SQL TO "PYCLE";
GRANT SELECT ON GV_$SESSION TO "PYCLE";
GRANT SELECT ON V_$FILESTAT TO "PYCLE";
GRANT SELECT ON V_$FLASHBACK_DATABASE_LOGFILE TO "PYCLE";
GRANT SELECT ON GV_$PARAMETER TO "PYCLE";
GRANT SELECT ON DBA_EXTENTS TO "PYCLE";
GRANT SELECT ON DBA_PROFILES TO "PYCLE";
GRANT SELECT ON DBA_ROLE_PRIVS TO "PYCLE";
GRANT SELECT ON DBA_HIST_OSSTAT TO "PYCLE";
GRANT SELECT ON DBA_HIST_SYSMETRIC_SUMMARY TO "PYCLE";
GRANT SELECT ON DBA_ALERT_HISTORY TO "PYCLE";
GRANT SELECT ON DBA_OBJECTS TO "PYCLE";
GRANT SELECT ON DBA_USERS TO "PYCLE";
GRANT SELECT ON DBA_JOBS_RUNNING TO "PYCLE";
GRANT SELECT ON DBA_SYS_PRIVS TO "PYCLE";
GRANT SELECT ON DBA_TAB_PRIVS TO "PYCLE";
GRANT SELECT ON DBA_TABLESPACES TO "PYCLE";
GRANT SELECT ON DBA_DATA_FILES TO "PYCLE";
GRANT SELECT ON DBA_FREE_SPACE TO "PYCLE";
GRANT SELECT ON DBA_SEGMENTS TO "PYCLE";
GRANT SELECT ON DBA_TEMP_FILES TO "PYCLE";
GRANT SELECT ON DBA_TABLES TO "PYCLE";
GRANT SELECT ON DBA_INDEXES TO "PYCLE";
GRANT SELECT ON DBA_IND_COLUMNS TO "PYCLE";
GRANT SELECT ON DBA_RECYCLEBIN TO "PYCLE";
GRANT SELECT ON DBA_TAB_PARTITIONS TO "PYCLE";
GRANT SELECT ON DBA_IND_PARTITIONS TO "PYCLE";
GRANT SELECT ON DBA_TAB_COLS TO "PYCLE";
GRANT SELECT ON DBA_SCHEDULER_JOBS TO "PYCLE";
GRANT SELECT ON DBA_AUTOTASK_CLIENT TO "PYCLE";
GRANT SELECT ON DBA_AUTOTASK_WINDOW_CLIENTS TO "PYCLE";
GRANT SELECT ON DBA_TAB_STATISTICS TO "PYCLE";
GRANT SELECT ON DBA_CONSTRAINTS TO "PYCLE";
GRANT SELECT ON DBA_CONS_COLUMNS TO "PYCLE";
GRANT SELECT ON DBA_HIST_SNAPSHOT TO "PYCLE";
GRANT EXECUTE ON "SYS"."DBMS_WORKLOAD_REPOSITORY" TO "PYCLE";
GRANT EXECUTE ON "SYS"."DBMS_ADVISOR" TO "PYCLE";
GRANT SELECT ON DBA_TABLESPACE_USAGE_METRICS TO "PYCLE";
GRANT SELECT ON V_$ACTIVE_SESSION_HISTORY TO "PYCLE";
GRANT SELECT ON V_$PGASTAT TO "PYCLE";
GRANT SELECT ON V_$RESTORE_POINT TO "PYCLE";
GRANT SELECT ON V_$SYSMETRIC TO "PYCLE";
GRANT SELECT ON V_$SYSTEM_PARAMETER TO "PYCLE";
```
或者直接赋予 select_catalog_role 角色
```sql
GRANT SELECT_CATALOG_ROLE TO "PYCLE";
```

- **Run pycle command**

  run pycle command would be easy and simple way, you don't need to give path to pycle.py to run.

  default values:

  ​ host = 127.0.0.1

  ​ port = 1521

  ​ sid = orcl

  ​ user = pycle

  ​ password = pycle

  ```shell
  # get help text
  $ pycle --help
  Usage: pycle [OPTIONS] COMMAND [ARGS]...

    A CLI utility to check some database

    example:

    pycle -h 172.16.2.91 -p 1521 -s ywptdata1 -u pycle -P pycle get-metric -m
    asm_size -v DATA

  Options:
    -h, --host TEXT    IP地址  [required]
    -p, --port TEXT    监听端口  [required]
    -s, --sid TEXT     实例SID  [required]
    -u, --user TEXT    用户名  [required]
    -P, --passwd TEXT  密码  [required]
    --help             Show this message and exit.

  Commands:
    discovery   获得多行值，返回json格式，供zabbix进行low level discovery采集
    get-metric  获取指标，返回单个值，供zabbix采集监控

  # get help text for chk-oracle
  pycle discovery --help
  Usage: pycle discovery [OPTIONS]

    获得多行值，返回json格式，供zabbix进行low level discovery采集

  Options:
    -d, --discovery-type TEXT  discovery类型  [required]
    --help                     Show this message and exit.
  ```

- Example

  Say i want to get a database logical size, run command like bellow

  ```shell
  $ pycle chk-oracle --host=172.16.1.204 --sid=shs --check=dbsize
  13667270656
  ```

## Dev Environments Configuration

Say you try to build your scripts, here is a brief introduction for how to get your environment done and build your CLI utility.

- Create Virtual env

  ```shell
  $ virtualenv --no-site-packages env
  ```

- `Click` installation

  ```shell
  $ pip install click
  ```

- `cx_Oracle` installation

  ```shell
  $ python -m pip install cx_Oracle --upgrade
  ```

  - Client side configuration

    After install cx_Oracle, package, you need to configure correctly your environment to use cx_Oracle. I'm using macOS, so check bellow content for how to configure client on macOS. for other platform, such as Windows, Linux, choose specific installation guide on this [url](https://cx-oracle.readthedocs.io/en/latest/installation.html#).

    1. Download Oracle instant client from [here](http://www.oracle.com/technetwork/topics/intel-macsoft-096467.html). Choose either a 64-bit or 32-bit package, matching your Python architecture.

    2. Unzip the package into a single directory that is accessible to your application. For example:

       ```shell
       mkdir -p /opt/oracle
       unzip instantclient-basic-macos.x64-12.2.0.1.0.zip
       ```

    3. Add links to `$HOME/lib` or `/usr/local/lib` to enable applications to find the library. For example:

       ```shell
       mkdir ~/lib
       ln -s /opt/oracle/instantclient_12_2/libclntsh.dylib ~/lib/
       ```

       Alternatively, copy the required OCI libraries. For example:

       ```shell
       mkdir ~/lib
       cp /opt/oracle/instantclient_12_2/{libclntsh.dylib.12.1,libclntshcore.dylib.12.1,libons.dylib,libnnz12.dylib,libociei.dylib} ~/lib/
       ```

       For Instant Client 11.2, the OCI libraries must be copied. For example:

       ```shell
       mkdir ~/lib
       cp /opt/oracle/instantclient_11_2/{libclntsh.dylib.11.1,libnnz11.dylib,libociei.dylib} ~/lib/
       ```

    4. If you intend to co-locate optional Oracle configuration files such as `tnsnames.ora`, `sqlnet.ora`or `oraaccess.xml` with Instant Client, then create a `network/admin` subdirectory. For example:

       ```shell
       mkdir -p /opt/oracle/instantclient_12_2/network/admin
       ```

       This is the default Oracle configuration directory for executables linked with this Instant Client.

       Alternatively, Oracle configuration files can be put in another, accessible directory. Then set the environment variable `TNS_ADMIN` to that directory name.

### How to Pack

If you wan to make your distribution package, you can check this instructions to learn how

Setup tools: <https://click.palletsprojects.com/en/7.x/setuptools/>

Python Packaging User Guide: https://packaging.python.org/#python-packaging-user-guide
