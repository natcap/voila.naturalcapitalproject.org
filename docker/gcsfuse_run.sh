#!/usr/bin/env bash
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START cloudrun_fuse_script]
#!/usr/bin/env bash
set -eo pipefail

echo "Mounting GCS Fuse."
gcsfuse --debug_gcs --debug_fuse "$BUCKET" "$MNT_DIR"
echo "Mounting completed."

exec /opt/conda/bin/voila \
    --port="$PORT" \
    --no-browser \
    --pool_size=4 \
    --preheat_kernel=True \
    --voila.ip=0.0.0.0 \
    --show_tracebacks=True /opt/app.ipynb

# [END cloudrun_fuse_script]
