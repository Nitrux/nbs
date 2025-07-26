#!/usr/bin/env python3

#############################################################################################################################################################################
#   The license used for this file and its contents is: BSD-3-Clause                                                                                                        #
#                                                                                                                                                                           #
#   Copyright <2025> <Uri Herrera <uri_herrera@nxos.org>>                                                                                                                   #
#                                                                                                                                                                           #
#   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:                          #
#                                                                                                                                                                           #
#    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.                                        #
#                                                                                                                                                                           #
#    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer                                      #
#       in the documentation and/or other materials provided with the distribution.                                                                                         #
#                                                                                                                                                                           #
#    3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software                    #
#       without specific prior written permission.                                                                                                                          #
#                                                                                                                                                                           #
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,                      #
#    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS                  #
#    BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE                 #
#    GOODS OR SERVICES; LOSS OF USE, DATA,   OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,                      #
#    STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.   #
#############################################################################################################################################################################

from pathlib import Path
import shutil
from threading import Lock

from nbs_cli.fetcher import get_latest_deb
from nbs_cli.extraction import extract_deb
from nbs_cli.utensils import cleanup_cache
# <---
# --->
def create_base_system(package_list, repos, cache_name="bootstrap", rootfs_path=Path("build/rootfs")):
    """
    Download and extract each package to its own cache dir, then merge into rootfs.
    Returns a dict summarizing success/failure.
    """
    cache_dir = Path.home() / ".cache/nbs-cli" / cache_name
    rootfs_path = Path(rootfs_path)
    log_lock = Lock()

    if rootfs_path.exists():
        print(f"🧹 Cleaning previous rootfs at {rootfs_path}")
        shutil.rmtree(rootfs_path)

    rootfs_path.mkdir(parents=True, exist_ok=True)

    summary = {
        "success": [],
        "failed": [],
        "skipped": []
    }

    for pkg in package_list:
        print(f"📦 Processing package: {pkg}")
        try:
            deb_path = get_latest_deb(pkg, repos, cache_name, log_lock=log_lock, quiet=False)
            if deb_path:
                extract_deb(deb_path, pkg, quiet=False)
                summary["success"].append(pkg)
            else:
                print(f"⚠️  Skipped (not found): {pkg}")
                summary["skipped"].append(pkg)
        except Exception as e:
            print(f"❌ Error processing {pkg}: {e}")
            summary["failed"].append(pkg)

    # -- Merge all per-package bootstrap dirs into final rootfs.

    merge_package_dirs_to_rootfs(cache_dir, rootfs_path)

    return summary


def merge_package_dirs_to_rootfs(cache_dir: Path, rootfs_path: Path):
    """
    Copy all files from ~/.cache/nbs-cli/<package>/bootstrap/ into the unified rootfs.
    """
    print("🗂️  Merging extracted package contents into rootfs...")
    for pkg_dir in cache_dir.iterdir():
        src = pkg_dir / "bootstrap"
        if src.exists():
            shutil.copytree(src, rootfs_path, dirs_exist_ok=True)
            print(f"✅ Merged: {src}")
        else:
            print(f"⚠️  Skipped missing: {src}")