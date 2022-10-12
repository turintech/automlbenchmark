#!/usr/bin/env bash
HERE=$(dirname "$0")
echo "creating local venv "
. ${HERE}/../shared/setup.sh ${HERE} true

#machine nexus.dataspartan.com
#	login chatterquant
#	password yUzy46I!eu5v

#[global]
#trusted-host = nexus.dataspartan.com
#extra-index-url = https://nexus.dataspartan.com/repository/pypi-external/simple

#cp ${HERE}/pipconf/pip.conf ${HERE}/venv
#cp ${HERE}/pipconf/.netrc ${HOME}

#${HERE}/venv/bin/pip install --no-cache-dir openml boto3 #	--extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external
#${HERE}/venv/bin/pip install evoml-client	--extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external
#${HERE}/venv/bin/pip install evoml-client	#--extra-index-url https://chatterquant:yUzy46I%5C%21eu5v@nexus.dataspartan.com/repository/pypi-external

#${HERE}/venv/bin/python -m pip install evoml_client[full]==0.1.4 evoml_pipeline_interface metaml --extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external/simple
${HERE}/venv/bin/python -m pip install metaml[all] evoml_client[full]==0.1.7 --extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external/simple
echo 'ec DONE'
${HERE}/venv/bin/python -m pip install evoml_pipeline_interface --extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external/simple
${HERE}/venv/bin/python -m pip install evoml_utils==0.6.21 --extra-index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external/simple
${HERE}/venv/bin/pip install --no-cache-dir openml boto3

#PIP install -r requirements.txt
#printf "Reqs done "
#
#printf "open ml done "
##PIP install evoml-client --index-url https://chatterquant:yUzy46I\!eu5v@nexus.dataspartan.com/repository/pypi-external
##PIP install evoml-client --index-url https://nexus.dataspartan.com/repository/pypi-all/simple

printf "ec done "

