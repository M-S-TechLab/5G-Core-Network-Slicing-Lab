# Test 04 — Nextcloud File Transfer over SST 1

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the core, gNB and both UEs

Execute `00-startup.md`; both `psi1` namespaces must exist.

## 2. Start Nextcloud and create test users for UE1 and UE2

1. Start Nextcloud and register the slice gateway IP as a trusted domain:
```bash
sudo snap start nextcloud
sudo snap services nextcloud
sudo nextcloud.occ config:system:set trusted_domains 1 --value="10.45.0.1"
```

2. Create the two accounts for the test UEs:
```bash
# Create user1 (assigned to UE1) with password 'nextclouduser1'
OC_PASS="nextclouduser1" sudo -E nextcloud.occ user:add --password-from-env user1

# Create user2 (assigned to UE2) with password 'nextclouduser2'
OC_PASS="nextclouduser2" sudo -E nextcloud.occ user:add --password-from-env user2
```

> **Note on Credentials:** `user1:nextclouduser1` and `user2:nextclouduser2` are demonstration credentials. If you choose different usernames or passwords when running the `user:add` command, substitute your values in the `curl` commands below.

## 3. Generate a 5 MiB test file

```bash
echo 'Test SST1 from UE1 to UE2' > test.txt
truncate -s 5M test.txt
ls -lh test.txt
```

## 4. Upload file as user1 from UE1 (SST 1)

Upload the file via WebDAV. Sostituisci `'user1:nextclouduser1'` con `'<USER1>:<PASS1>'` se hai usato credenziali personalizzate:

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 \
  curl --fail --show-error -u 'user1:nextclouduser1' \
  -T test.txt 'http://10.45.0.1/remote.php/dav/files/user1/test.txt'
```

## 5. Share the uploaded file with user2 (OCS API)

Share the file with the second user. Sostituisci `'user1:nextclouduser1'` e `'shareWith=user2'` con i tuoi utenti:

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 \
  curl --fail --show-error -u 'user1:nextclouduser1' \
  -H 'OCS-APIRequest: true' -X POST \
  -d 'path=/test.txt' -d 'shareType=0' -d 'shareWith=user2' \
  'http://10.45.0.1/ocs/v2.php/apps/files_sharing/api/v1/shares'
```

## 6. Download file from UE2 (SST 1)

Download the shared file via WebDAV using user2's credentials. Sostituisci `'user2:nextclouduser2'` con `'<USER2>:<PASS2>'`:

```bash
sudo ip netns exec ueransim-999700000000002-internet-psi1 \
  curl --fail --show-error -u 'user2:nextclouduser2' \
  -o received-test.txt \
  'http://10.45.0.1/remote.php/dav/files/user2/test.txt'
```

The shared file must be visible in user2's files for this WebDAV URL to work. If the share is only available through a different share mount path, check Nextcloud first.

## 7. Compare original and downloaded hashes

```bash
sha256sum test.txt received-test.txt
```

The report says both transfers succeeded and SHA-256 matched; actual hashes and transfer timings were not provided.
