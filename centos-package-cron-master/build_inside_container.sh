#!/bin/bash

set -e
set -x

cd /tmp
# Have to copy files away from our host volume because of Docker<->rpmbuild permission errors on CentOS6
cp -v /code/$1 .
cp -v /code/centos-package-cron.spec .
SPEC_FILE=centos-package-cron.spec

if [ "$CENTOS" == "centos7" ]
then
  # rpmlint on centos6 complains a lot
  rpmlint $SPEC_FILE
fi

sudo yum-builddep -y --disablerepo=updates $SPEC_FILE
rpmbuild -ba --verbose -D "_topdir /tmp/rpm" -D "_sourcedir `pwd`" -D "_builddir /tmp/rpm" $SPEC_FILE
mkdir -p /code/built_rpms
cp -v -R /tmp/rpm/RPMS /code/built_rpms
cp -v -R /tmp/rpm/SRPMS /code/built_rpms
