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
# that shows the new merged pull requests.
#
# Must be run from the root of a repository, unless you specify the submodule
# paths on the command line.
#
# If the -n option is given the script will not pull new commits itself, but
# will only commit the submodule update with the generated commit message.

pull=1

while getopts ":nh" opt; do
    case $opt in
        n)
            pull=0
            ;;
        h)
            echo "usage: $0 [-n] [PATH...]"
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done

shift $(($OPTIND-1))

if [[ $@ ]]; then
    paths="$@"
else
    paths=$(echo submodules/*)
fi

for S in $paths; do
    [ -d $S ] || continue
    if [ $pull -eq 1 ]; then
        echo "Updating $S"
        git -C $S checkout --quiet master
        git -C $S pull --quiet origin master
    fi
    if ! git diff --quiet $S; then
        (echo "update $(basename $S)"; echo; git submodule summary $S) | git commit -F- $S
    fi
done
