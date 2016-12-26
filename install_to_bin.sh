#!/bin/sh

CWD=$(pwd)
SCRIPT_NAME="backup.py"
CMDNAME="backup"

chmod a+x "${CWD}/${SCRIPT_NAME}"
mkdir -p ${HOME}/bin/
chmod 755 ${HOME}/bin/ -R

if [ ! -f ${HOME}/bin/${CMDNAME} ];then
	ln -s  "${CWD}/${SCRIPT_NAME}" "${HOME}/bin/${CMDNAME}"
else
	echo "[INFO] Exist Command: ${HOME}/bin/${CMDNAME}"
fi

profile="$HOME/.bash_profile"
if [ ! -f ${profile} ];then
	profile="$HOME/.profile"
fi

echo "$PATH" | grep "${HOME}/bin" > /dev/null 2>&1
if [ $? -ne 0 ];then
	cat $profile | grep "${HOME}/bin" > /dev/null 2>&1
	if [ $? -ne 0 ];then
		echo "export PATH=${HOME}/bin:$PATH" >> ${profile}
	else
		echo "[INFO] Exist Bin Path: ${HOME}/bin"
	fi
else
	echo "[INFO] Exist Bin Path(${HOME}/bin) In PATH: ${PATH}"
fi
