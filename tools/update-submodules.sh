#!/bin/bash -eu
################################################################
#
#        Copyright 2013, Big Switch Networks, Inc.
#
# Licensed under the Eclipse Public License, Version 1.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#        http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.
#
################################################################

# Updates each submodule to origin/master and writes a nice commit message
# that shows the new merged pull requests. Must be run from the root of a
# repository.

for S in submodules/*; do
    [ -d $S ] || continue
    echo "Updating $S"
    git -C $S checkout --quiet master
    git -C $S pull --quiet origin master
    if ! git diff --quiet $S; then
        (echo "update $(basename $S)"; echo; git submodule summary $S) | git commit -F- $S
    fi
done
