# Test 04 — Nextcloud File Transfer over SST 1

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the core, gNB and both UEs

Execute `00-startup.md`; both `psi1` namespaces must exist.

## 2. Start and check Nextcloud

```bash
sudo snap start nextcloud
sudo snap services nextcloud
sudo nextcloud.occ config:system:get trusted_domains
```

The laboratory uses WebDAV over HTTP with the SST 1 gateway `10.45.0.1`.

## 3. Generate a 5 MiB test file

```bash
echo 'Test SST1 from UE1 to UE2' > test.txt
truncate -s 5M test.txt
ls -lh test.txt
```

## 4. Upload as user1 from UE1 (SST 1)

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 \
  curl --fail --show-error -u 'user1:nextclouduser1' \
  -T test.txt 'http://10.45.0.1/remote.php/dav/files/user1/test.txt'
```

The credentials are **laboratory examples previously used in conversation**; replace them if the installed WebUI account passwords differ.

## 5. Share the uploaded file with user2 (OCS API)

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 \
  curl --fail --show-error -u 'user1:nextclouduser1' \
  -H 'OCS-APIRequest: true' -X POST \
  -d 'path=/test.txt' -d 'shareType=0' -d 'shareWith=user2' \
  'http://10.45.0.1/ocs/v2.php/apps/files_sharing/api/v1/shares'
```

## 6. Download from UE2 (SST 1)

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
