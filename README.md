1. for Oracle check, need create user `pycle` and grant query privileges on some dictionary and v$ view
create user `pycle` DDL:
```
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
```

2. for check oracle utilities, cx_oracle module needs oracle baseclient configured correctly on your machine. so you need to install oracle client(which you can download a instant client from this website: https://www.oracle.com/technetwork/database/database-technologies/instant-client/downloads/index.html), follow the website's guide to configure, such as NLS_LANG, PATH envirement variables,
for Linux Server, you can install rpm package directly