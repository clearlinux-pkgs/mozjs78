#
# Inspired by the Arch Linux equivalent package.....
#
Name     : mozjs78
Version  : 78.15.0
Release  : 27
URL      : https://archive.mozilla.org/pub/firefox/releases/78.15.0esr/source/firefox-78.15.0esr.source.tar.xz
Source0  : https://archive.mozilla.org/pub/firefox/releases/78.15.0esr/source/firefox-78.15.0esr.source.tar.xz
Group    : Development/Tools
License  : Apache-2.0 BSD-2-Clause BSD-3-Clause BSD-3-Clause-Clear GPL-2.0 LGPL-2.0 LGPL-2.1 MIT MPL-2.0-no-copyleft-exception
Requires: mozjs78-bin
Requires: mozjs78-lib
Requires: pypi-psutil
Requires: pypi-pyopenssl
Requires: pypi-pyasn1
Requires: pypi-wheel
BuildRequires : icu4c-dev
BuildRequires : nspr-dev
BuildRequires : pypi-pbr
BuildRequires : pypi-pip
BuildRequires : pkgconfig(libffi)
BuildRequires : pkgconfig(x11)
BuildRequires : pypi-psutil
BuildRequires : python3-core
BuildRequires : python3-dev
BuildRequires : pypi-setuptools
BuildRequires : zlib-dev
BuildRequires : autoconf213
BuildRequires : readline-dev
BuildRequires : ncurses-dev
BuildRequires : rustc
BuildRequires : llvm-dev
Summary: mozjs

Patch1: fix-soname.patch
Patch2: copy-headers.patch
Patch3: init_patch.patch
Patch4: emitter.patch
Patch5: spidermonkey_checks_disable.patch
Patch6: not-a-browser.patch
Patch7: 0001-Fixes-for-Python-3.10.patch
Patch8: 0002-Fixes-for-Rust-1.56.patch

%description
JavaScript interpreter and libraries - Version 78

%package bin
Summary: bin components for the mozjs78 package.
Group: Binaries

%description bin
bin components for the mozjs78 package.


%package dev
Summary: dev components for the mozjs78 package.
Group: Development
Requires: mozjs78-lib
Requires: mozjs78-bin
Provides: mozjs78-devel

%description dev
dev components for the mozjs78 package.


%package lib
Summary: lib components for the mozjs78 package.
Group: Libraries

%description lib
lib components for the mozjs78 package.


%prep
%setup -q -n firefox-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

# use system zlib for perf
rm -rf ../../modules/zlib

pushd ..
cp -a firefox-%{version} buildavx2
popd

%build
export http_proxy=http://127.0.0.1:9/
export https_proxy=http://127.0.0.1:9/
export no_proxy=localhost,127.0.0.1,0.0.0.0
export LANG=C
export SOURCE_DATE_EPOCH=1501084420
export CFLAGS="-Os -falign-functions=4 -fno-semantic-interposition -fno-signed-zeros -fstack-protector -mtune=skylake "
export FCFLAGS="-O3 -falign-functions=32 -fno-semantic-interposition "
export FFLAGS="$CFLAGS -O3 -falign-functions=32 -fno-semantic-interposition "
export CXXFLAGS="-Os -falign-functions=4 -fno-semantic-interposition -fno-signed-zeros -fstack-protector -mtune=skylake"
export AUTOCONF="/usr/bin/autoconf213"
CFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
CXXFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
export CC=gcc CXX=g++ PYTHON=/usr/bin/python

pushd js/src

autoconf213
%configure --disable-static \
    --prefix=/usr \
    --disable-debug \
    --enable-debug-symbols \
    --disable-strip \
    --disable-jemalloc \
    --enable-optimize="-O3" \
    --enable-posix-nspr-emulation \
    --enable-readline \
    --enable-release \
    --enable-shared-js \
    --enable-tests \
    --with-intl-api \
    --with-system-zlib \
    --with-x \
    --program-suffix=78 \
    --without-system-icu

make -s %{?_smp_mflags}
popd

pushd ../buildavx2/js/src
export CFLAGS="-O3 -fno-semantic-interposition -fno-signed-zeros -march=x86-64-v3 -mno-vzeroupper -fstack-protector -mtune=skylake"
export CXXFLAGS="-O3 -fno-semantic-interposition -fno-signed-zeros -march=x86-64-v3 -mno-vzeroupper -fstack-protector -mtune=skylake"
CFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
CXXFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
export CC=gcc CXX=g++ PYTHON=/usr/bin/python
autoconf213
%configure --disable-static \
    --prefix=/usr \
    --disable-debug \
    --enable-debug-symbols \
    --disable-strip \
    --disable-jemalloc \
    --enable-optimize="-O3 -march=x86-64-v3" \
    --enable-posix-nspr-emulation \
    --enable-readline \
    --enable-release \
    --enable-shared-js \
    --enable-tests \
    --with-intl-api \
    --with-system-zlib \
    --with-x \
    --program-suffix=78 \
    --without-system-icu
make -s %{?_smp_mflags}    
popd



%install
export SOURCE_DATE_EPOCH=1501084420
rm -rf %{buildroot}
pushd js/src
%make_install
popd

pushd ../buildavx2/js/src
%make_install_v3
popd


rm %{buildroot}*/usr/lib64/*.ajs

cp %{buildroot}/usr/lib64/libmozjs-78.so %{buildroot}/usr/lib64/libmozjs-78.so.0
cp %{buildroot}-v3/usr/lib64/libmozjs-78.so %{buildroot}-v3/usr/lib64/libmozjs-78.so.0

/usr/bin/elf-move.py avx2 %{buildroot}-v3 %{buildroot} %{buildroot}/usr/share/clear/filemap/filemap-%{name}

%files
%defattr(-,root,root,-)

%files bin
%defattr(-,root,root,-)
/usr/bin/js78
/usr/bin/js78-config
/usr/share/clear/filemap/filemap-*
/usr/share/clear/optimized-elf/bin*

%files dev
%defattr(-,root,root,-)
/usr/include/mozjs-78/
/usr/lib64/pkgconfig/mozjs-78.pc

%files lib
%defattr(-,root,root,-)
/usr/lib64/glibc-hwcaps/x86-64-v3/libmozjs-78.so
/usr/lib64/glibc-hwcaps/x86-64-v3/libmozjs-78.so.0
/usr/lib64/libmozjs-78.so
/usr/lib64/libmozjs-78.so.0
