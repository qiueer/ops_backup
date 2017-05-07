## 功能
```
用于对目录、文件执行备份；  
同时根据配置项决定是否压缩，以及保留的备份份数；  
适用于linux、windows系统；  
```

## 原理
```
使用rsync命令对目录、文件进行备份；  
使用tarfile对目录、文件进行压缩归档；  
使用rm(window是del/rd)对备份目录进行清理；  
```

## 配置说明
```
[linux]      ## 每个备份任务的唯一ID  
srcfiles = /home/superman/cmdb;/home/superman/ops_backup ## 备份目录(文件)  
destdir = /tmp/superman  ## 备份目录(文件)存放目录  
func = 备份CMDB以及本py脚本所在目录 ## 功能说明  
excludes = .svn-base;.svn  ## 需要排除的目录(文件)  
zip = 1  ## 是否压缩：1压缩，0不压缩
keep = 10  ## 保留份数  
timeout = 600 ## 执行备份任务预估所需时间，超过此时间会终止任务，不配置则会一直执行备份直至完成  
  
[windows]  ## 同上  
func = 备份PYTHON资源 ## 同上  
srcfiles = E:\python资源    ## 同上  
destdir = d:\superman  ## 同上    
excludes = .svn-base;.svn  ## 同上    
zip = 1  ## 同上    
keep = 10  ## 同上    
```

## 用法
```
python backup.py   
Usage: backup.py [options]  
  
Options:  
  -h, --help            show this help message and exit  
  -i ID, --id=ID        which id to backup, if none, backup all  
  -c CONFFILE, --conf=CONFFILE  
                        configure file  
  -l, --list            list all the configure  
  -d, --debug           if open debug module  
```
