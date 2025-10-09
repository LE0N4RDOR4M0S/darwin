#!/bin/sh
set -e

SSH_KEY_PATH=${SSH_KEY_PATH:-/root/.ssh/id_rsa}

if [ -n "${SSH_PRIVATE_KEY_B64}" ]; then
  echo "SSH_PRIVATE_KEY_B64 is set, attempting to create SSH key at ${SSH_KEY_PATH}"
  mkdir -p "$(dirname "${SSH_KEY_PATH}")" 2>/dev/null || true

  TMP_DEC="$(mktemp /tmp/id_rsa.dec.XXXXXX)"
  if printf '%s' "${SSH_PRIVATE_KEY_B64}" | base64 -d > "${TMP_DEC}" 2>/tmp/base64.err; then
    chmod 600 "${TMP_DEC}" || true
    if cp "${TMP_DEC}" "${SSH_KEY_PATH}" 2>/dev/null; then
      KEY_TO_USE="${SSH_KEY_PATH}"
      chmod 600 "${KEY_TO_USE}" || true
      chown root:root "${KEY_TO_USE}" || true
    else
      echo "Warning: cannot write to ${SSH_KEY_PATH} (read-only). Using ${TMP_DEC} instead."
      KEY_TO_USE="${TMP_DEC}"
    fi

    export GIT_SSH_COMMAND="ssh -i ${KEY_TO_USE} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    echo "GIT_SSH_COMMAND set (from env), key: ${KEY_TO_USE}"
  else
    echo "ERROR: failed to decode SSH_PRIVATE_KEY_B64 (invalid base64). Details:" >&2
    cat /tmp/base64.err 2>/dev/null >&2 || true
    rm -f "${TMP_DEC}" 2>/dev/null || true
    echo "Continuing without SSH key configured. If you expect a key, ensure SSH_PRIVATE_KEY_B64 contains a valid base64 string of your private key." >&2
  fi
else
  if [ -f "${SSH_KEY_PATH}" ]; then
    echo "SSH key file already present at ${SSH_KEY_PATH}; copying to a secure temp file to ensure correct permissions"
    TMP_KEY="$(mktemp /tmp/id_rsa.XXXXXX)"
    if cp "${SSH_KEY_PATH}" "${TMP_KEY}" 2>/dev/null; then
      chmod 600 "${TMP_KEY}" || true
      chown root:root "${TMP_KEY}" || true
      KEY_TO_USE="${TMP_KEY}"
      echo "Copied mounted key to ${TMP_KEY} and set permissions"
    else
      # Fall back to using the mounted key if copy fails (unlikely if readable)
      echo "Warning: failed to copy mounted key; attempting to use mounted key directly"
      chmod 600 "${SSH_KEY_PATH}" || true
      KEY_TO_USE="${SSH_KEY_PATH}"
    fi

    export GIT_SSH_COMMAND="ssh -i ${KEY_TO_USE} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    echo "GIT_SSH_COMMAND set (from mounted file), key: ${KEY_TO_USE}"
  else
    echo "SSH_PRIVATE_KEY_B64 not provided and no key file at ${SSH_KEY_PATH}; git push via SSH will not be available."
  fi
fi

if [ -n "${GENERATOR_GIT_USER_NAME}" ]; then
  git config --global user.name "${GENERATOR_GIT_USER_NAME}" || true
fi
if [ -n "${GENERATOR_GIT_USER_EMAIL}" ]; then
  git config --global user.email "${GENERATOR_GIT_USER_EMAIL}" || true
fi

exec "$@"
