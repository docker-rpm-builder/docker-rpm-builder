#!/bin/bash
SIGN_KEY="$1"
shift
echo -e "asdasd\n" | setsid rpm --define '__gpg_sign_cmd %{__gpg} gpg --batch --no-verbose --no-armor --passphrase-fd 3 --no-secmem-warning -u "%{_gpg_name}" -sbo %{__signature_filename} %{__plaintext_filename}' --define "_gpg_name ${SIGN_KEY}" --define '_signature gpg' --resign $*
