<!--
 * @Description: In User Settings Edit
 * @Author: your name
 * @Date: 2019-04-08 15:51:04
 * @LastEditTime: 2019-08-28 12:17:49
 * @LastEditors: Please set LastEditors
 -->

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

  pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'

Options:
  --help  Show this message and exit.

Commands:
  chk-oracle  查询Oracle
```

Or you can just download `pycle.py` scripts, but in this way you need to resolve dependency package by yourself

run bellow command

```shell
# install dependency package
$ pip install click
$ pip install cx_Oracle

# run test
$ python pycle.py --help
Usage: pycle.py [OPTIONS] COMMAND [ARGS]...

  A CLI utility to check some database

  example:

  pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'

Options:
  --help  Show this message and exit.

Commands:
  chk-oracle  查询Oracle
```

## How to Use

There are two way to use this utility, run `pycle` command or run `pycle.py` scripts directly. Before use to check Oracle database, you need create a user `pycle`, bellow is creation script

```shell
CREATE USER "PYCLE" IDENTIFIED BY "pycle";
grant "CONNECT" TO "PYCLE";
grant select on v_$instance to "PYCLE";
grant select on v_$session to "PYCLE";
grant select on v_$sysstat to "PYCLE";
grant select on v_$system_event to "PYCLE";
grant select on v_$asm_diskgroup to "PYCLE";
grant select on v_$sys_time_model to "PYCLE";
grant select on v_$parameter to "PYCLE";
grant select on v_$latch to "PYCLE";
grant select on v_$latch_children to "PYCLE";
grant select on v_$sgastat to "PYCLE";
grant select on v_$resource_limit to "PYCLE";
grant select on v_$datafile to "PYCLE";
grant select on v_$px_session to "PYCLE";
grant select on v_$dispatcher to "PYCLE";
grant select on v_$shared_server to "PYCLE";
grant select on v_$tablespace to "PYCLE";
grant select on v_$archived_log to "PYCLE";
grant select on v_$rman_status to "PYCLE";
grant select on v_$memory_dynamic_components to "PYCLE";
grant select on v_$log to "PYCLE";
grant select on v_$event_name to "PYCLE";
grant select on v_$archive_dest to "PYCLE";
grant select on v_$log_history to "PYCLE";
grant select on v_$database to "PYCLE";
grant select on v_$osstat to "PYCLE";
grant select on v_$process to "PYCLE";
grant select on v_$temp_space_header to "PYCLE";
grant select on v_$temp_extent_pool  to "PYCLE";
grant select on v_$asm_disk to "PYCLE";
grant select on v_$asm_file to "PYCLE";
grant select on v_$recovery_file_dest to "PYCLE";
grant select on v_$flash_recovery_area_usage to "PYCLE";
grant select on v_$session to "PYCLE";
grant select on v_$transaction to "PYCLE";
grant select on v_$rollname to "PYCLE";
grant select on v_$rollstat to "PYCLE";
grant select on v_$sort_usage to "PYCLE"
grant select on v_$db_object_cache to "PYCLE";
grant select on v_$sqlarea to "PYCLE";
grant select on v_$sesstat to "PYCLE";
grant select on v_$statname to "PYCLE";
grant select on dba_alert_history to "PYCLE";
grant select on dba_objects to "PYCLE";
grant select on dba_users to "PYCLE";
grant select on dba_jobs_running to "PYCLE";
grant select on dba_sys_privs to "PYCLE";
grant select on dba_tab_privs to "PYCLE";
grant select on dba_tablespaces to "PYCLE";
grant select on dba_data_files to "PYCLE";
grant select on dba_free_space to "PYCLE";
grant select on dba_segments to "PYCLE";
grant select on dba_temp_files to "PYCLE";
grant select on dba_tables to "PYCLE";
grant select on dba_indexes to "PYCLE";
grant select on dba_ind_columns to "PYCLE";
grant select on dba_recyclebin to "PYCLE";
grant select on dba_tab_partitions to "PYCLE";
grant select on dba_ind_partitions to "PYCLE";
grant select on dba_tab_cols to "PYCLE";
grant select on dba_scheduler_jobs to "PYCLE";
grant select on dba_autotask_client to "PYCLE";
grant select on DBA_AUTOTASK_WINDOW_CLIENTS to "PYCLE";
grant select on dba_tab_statistics to "PYCLE";
grant select on dba_constraints to "PYCLE";
grant select on dba_cons_columns to "PYCLE";
```

- **Run pycle command**

  run pycle command would be easy and simple way, you don't need to give path to pycle.py to run. All options for chk-oracle command get a default value

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

    pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'

  Options:
    --help  Show this message and exit.

  Commands:
    chk-oracle  查询Oracle

  # get help text for chk-oracle
  pycle chk-oracle --help
  echo first
  Usage: pycle chk-oracle [OPTIONS]

    查询Oracle

  Options:
    -h, --host TEXT                 数据库IP地址  [required]
    -p, --port TEXT                 数据库监听端口  [required]
    -s, --sid TEXT                  数据库实例SID  [required]
    -u, --user TEXT                 数据库用户名  [required]
    -P, --passwd TEXT               用户密码  [required]
    -c, --check [dbversion|dbsize|check_active|read_cache_hit_ratio|disk_sorts_ratio|count_of_active_users|size_of_user_data|dbfilesize|dbuptime|usercommits|userrollback|deadlocks|redowrites|tablescans|tablerowscans|indexffs|hardparseratio|netset|netrecv|netroundtrips|currentloggons|lastarch|lastapplyarch|freebuffwaits|busybuffwaits|logswitcompletion|logfilesync|logparallelwrite|enqueue|dbseqreadwait|dbscatteredread|dbsinglewrite|dbparallelwrite|directpathread|directpathwrite|latchfree|tablespace|tablespaceinuse]
                                    查询目标
    -C, --checkparam TEXT           查询参数
    --help                          Show this message and exit.
  ```

- **Run pycle.py script**

  To run pycle.py script is a little different from run pycle command

  ```shell
  $ python pycle.py --help
  Usage: pycle.py [OPTIONS] COMMAND [ARGS]...

    A CLI utility to check some database

    example:

    pycle chk-oracle --host='127.0.0.1' --port='1521', --sid='orcl'

  Options:
    --help  Show this message and exit.

  Commands:
    chk-oracle  查询Oracle

  $ python pycle/pycle.py chk-oracle --help
  echo first
  Usage: pycle.py chk-oracle [OPTIONS]

    查询Oracle

  Options:
    -h, --host TEXT                 数据库IP地址  [required]
    -p, --port TEXT                 数据库监听端口  [required]
    -s, --sid TEXT                  数据库实例SID  [required]
    -u, --user TEXT                 数据库用户名  [required]
    -P, --passwd TEXT               用户密码  [required]
    -c, --check [dbversion|dbsize|check_active|read_cache_hit_ratio|disk_sorts_ratio|count_of_active_users|size_of_user_data|dbfilesize|dbuptime|usercommits|userrollback|deadlocks|redowrites|tablescans|tablerowscans|indexffs|hardparseratio|netset|netrecv|netroundtrips|currentloggons|lastarch|lastapplyarch|freebuffwaits|busybuffwaits|logswitcompletion|logfilesync|logparallelwrite|enqueue|dbseqreadwait|dbscatteredread|dbsinglewrite|dbparallelwrite|directpathread|directpathwrite|latchfree|tablespace|tablespaceinuse]
                                    查询目标
    -C, --checkparam TEXT           查询参数
    --help                          Show this message and exit.
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
