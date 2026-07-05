SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;

-- The CN baseline mounted by doc/tutorial_resources/oai-cn5g/docker-compose.yaml
-- defines AuthenticationSubscription and SessionManagementSubscriptionData,
-- but it does not define the legacy `users` table from ci-scripts/yaml_files/5g_rfsimulator/oai_db.sql.
-- Keep this overlay aligned with the actual CN schema to avoid failing MySQL init.

INSERT INTO `AuthenticationSubscription`
(`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`)
VALUES
('001010000000001', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{"sqn": "000000000000", "sqnScheme": "NON_TIME_BASED", "lastIndexes": {"ausf": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000001'),
('001010000000002', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{"sqn": "000000000000", "sqnScheme": "NON_TIME_BASED", "lastIndexes": {"ausf": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000002')
ON DUPLICATE KEY UPDATE
  authenticationMethod=VALUES(authenticationMethod),
  encPermanentKey=VALUES(encPermanentKey),
  protectionParameterId=VALUES(protectionParameterId),
  sequenceNumber=VALUES(sequenceNumber),
  authenticationManagementField=VALUES(authenticationManagementField),
  algorithmId=VALUES(algorithmId),
  encOpcKey=VALUES(encOpcKey),
  supi=VALUES(supi);

INSERT INTO `SessionManagementSubscriptionData`
(`ueid`, `servingPlmnid`, `singleNssai`, `dnnConfigurations`)
VALUES
('001010000000001', '00101', '{"sst": 1, "sd": "FFFFFF"}', '{"oai":{"pduSessionTypes":{ "defaultSessionType": "IPV4"},"sscModes": {"defaultSscMode": "SSC_MODE_1"},"5gQosProfile": {"5qi": 6,"arp":{"priorityLevel": 15,"preemptCap": "NOT_PREEMPT","preemptVuln":"PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"1000Mbps", "downlink":"1000Mbps"},"staticIpAddress":[{"ipv4Addr": "10.0.0.2"}]},"ims":{"pduSessionTypes":{ "defaultSessionType": "IPV4V6"},"sscModes": {"defaultSscMode": "SSC_MODE_1"},"5gQosProfile": {"5qi": 2,"arp":{"priorityLevel": 15,"preemptCap": "NOT_PREEMPT","preemptVuln":"PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"1000Mbps", "downlink":"1000Mbps"}}}'),
('001010000000002', '00101', '{"sst": 1, "sd": "FFFFFF"}', '{"oai":{"pduSessionTypes":{ "defaultSessionType": "IPV4"},"sscModes": {"defaultSscMode": "SSC_MODE_1"},"5gQosProfile": {"5qi": 6,"arp":{"priorityLevel": 15,"preemptCap": "NOT_PREEMPT","preemptVuln":"PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"1000Mbps", "downlink":"1000Mbps"},"staticIpAddress":[{"ipv4Addr": "10.0.0.3"}]},"ims":{"pduSessionTypes":{ "defaultSessionType": "IPV4V6"},"sscModes": {"defaultSscMode": "SSC_MODE_1"},"5gQosProfile": {"5qi": 2,"arp":{"priorityLevel": 15,"preemptCap": "NOT_PREEMPT","preemptVuln":"PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"1000Mbps", "downlink":"1000Mbps"}}}')
ON DUPLICATE KEY UPDATE
  singleNssai=VALUES(singleNssai),
  dnnConfigurations=VALUES(dnnConfigurations);

COMMIT;
