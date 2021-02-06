#!/bin/bash

set -e
set -o pipefail

PKG=mozjs78

git pull --ff-only
VERSION=$(curl -sSf https://archive.mozilla.org/pub/firefox/releases/ \
	    | grep href \
	    | cut -f3 -d">" \
	    | cut -f1 -d"/" \
	    | sed -nr 's/^(78\.[0-9.]+)esr/\1/p' \
	    | sort -t . -k 1,1n -k 2,2n -k 3,3n -k 4,4n \
	    | tail -1)

if [[ -z "${VERSION}" ]]; then
    echo "Unable to find version upstream."
    exit 1
fi

CURRENT_VERSION=$(grep "^Version" $PKG.spec | cut -f4 -d" ")

if [[ v"${CURRENT_VERSION}" == v"${VERSION}" ]]; then
	exit 2
fi

sed -e "s/##VERSION##/${VERSION}/g" $PKG.spec.in > $PKG.spec
make generateupstream || exit 3

make bumpnogit
git add $PKG.spec Makefile release upstream
git commit -s -m "Update to ${VERSION}"
make koji