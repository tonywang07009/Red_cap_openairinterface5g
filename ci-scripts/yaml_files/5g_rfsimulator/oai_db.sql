-- OAI 5G Core Database Schema (Hybrid Fix)
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- ==========================================
-- 1. AMF 吵著要的 users 表 (為了相容性或簡易模式)
-- ==========================================
CREATE TABLE IF NOT EXISTS `users` (
  `imsi` varchar(15) NOT NULL,
  `msisdn` varchar(46) DEFAULT NULL,
  `imei` varchar(15) DEFAULT NULL,
  `imei_sv` varchar(2) DEFAULT NULL,
  `ms_ps_status` enum('PURGED','NOT_PURGED') DEFAULT 'PURGED',
  `rau_tau_timer` int(10) unsigned DEFAULT '120',
  `ue_ambr_ul` bigint(20) unsigned DEFAULT '50000000',
  `ue_ambr_dl` bigint(20) unsigned DEFAULT '100000000',
  `access_restriction` int(10) unsigned DEFAULT '60',
  `mme_cap` int(10) unsigned zerofill DEFAULT NULL,
  `mmeidentity_idmmeidentity` int(11) NOT NULL DEFAULT '0',
  `key` varbinary(16) NOT NULL DEFAULT '0',
  `RFSP-Index` smallint(5) unsigned NOT NULL DEFAULT '1',
  `urrp_mme` tinyint(1) NOT NULL DEFAULT '0',
  `sqn` bigint(20) unsigned zerofill NOT NULL,
  `rand` varbinary(16) NOT NULL,
  `OPc` varbinary(16) DEFAULT NULL,
  PRIMARY KEY (`imsi`,`mmeidentity_idmmeidentity`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- 插入 users 資料 (對應您的 UE: 001010000000001 ~ 004)
INSERT INTO `users` VALUES 
('001010000000001','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000002','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000003','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000004','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000005','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000006','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000007','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000008','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000009','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000010','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000011','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000012','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000013','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000014','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000015','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000016','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000017','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000018','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000019','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000020','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000021','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000022','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000023','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000024','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000025','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000026','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000027','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1),
('001010000000028','1','55000000000000',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x00,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',0xc42449363bbad02b66d16bc975d77cc1)
ON DUPLICATE KEY UPDATE 
  ue_ambr_ul=VALUES(ue_ambr_ul); -- 如果已經存在就不報錯，簡單更新一下


-- ==========================================
-- 2. 標準 5G Core 表格 (AuthenticationSubscription 等)
-- ==========================================

CREATE TABLE IF NOT EXISTS `AuthenticationSubscription` (
  `ueid` varchar(20) NOT NULL,
  `authenticationMethod` varchar(25) NOT NULL,
  `encPermanentKey` varchar(50) DEFAULT NULL,
  `protectionParameterId` varchar(50) DEFAULT NULL,
  `sequenceNumber` json DEFAULT NULL,
  `authenticationManagementField` varchar(50) DEFAULT NULL,
  `algorithmId` varchar(50) DEFAULT NULL,
  `encOpcKey` varchar(50) DEFAULT NULL,
  `encTopcKey` varchar(50) DEFAULT NULL,
  `vectorGenerationInHss` tinyint(1) DEFAULT NULL,
  `n5gcAuthMethod` varchar(15) DEFAULT NULL,
  `rgAuthenticationInd` tinyint(1) DEFAULT NULL,
  `supi` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ueid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- 5g 用戶訂閱戶
INSERT INTO `AuthenticationSubscription`
(`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`)
 VALUES
('001010000000001', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000001'),
('001010000000002', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000002'),
('001010000000003', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000003'),
('001010000000004', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000004'),
('001010000000005', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000005'),
('001010000000006', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000006'),
('001010000000007', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000007'),
('001010000000008', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000008'),
('001010000000009', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000009'), 
('001010000000010', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000010'),
('001010000000011', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000011'),
('001010000000012', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000012'),
('001010000000013', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000013'),
('001010000000014', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000014'),
('001010000000015', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000015'),
('001010000000016', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000016'),
('001010000000017', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000017'),
('001010000000018', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000018'),
('001010000000019', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000019'),
('001010000000020', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000020'),
('001010000000021', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000021'),
('001010000000022', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000022'),
('001010000000023', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000023'),
('001010000000024', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000024'),
('001010000000025', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000025'),
('001010000000026', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000026'),
('001010000000027', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000027'),
('001010000000028', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000028')
ON DUPLICATE KEY UPDATE 
  authenticationMethod=VALUES(authenticationMethod);


CREATE TABLE IF NOT EXISTS `SessionManagementSubscriptionData` (
  `ueid` varchar(15) NOT NULL,
  `servingPlmnid` varchar(15) NOT NULL,
  `singleNssai` json NOT NULL,
  `dnnConfigurations` json DEFAULT NULL,
  `internalGroupIds` json DEFAULT NULL,
  `sharedVnGroupDataIds` json DEFAULT NULL,
  `sharedDnnConfigurationsId` varchar(50) DEFAULT NULL,
  `odbPacketServices` json DEFAULT NULL,
  `traceData` json DEFAULT NULL,
  `sharedTraceDataId` varchar(50) DEFAULT NULL,
  `expectedUeBehavioursList` json DEFAULT NULL,
  `suggestedPacketNumDlList` json DEFAULT NULL,
  `3gppChargingCharacteristics` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ueid`,`servingPlmnid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 這邊是資費方案與 IP 分配」(Session Management) 簡單來說就是有繳錢才給你網路
INSERT INTO `SessionManagementSubscriptionData` 
(`ueid`, `servingPlmnid`, `singleNssai`, `dnnConfigurations`) 
VALUES
('001010000000001', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.2\"}]}}'),
('001010000000002', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.3\"}]}}'),
('001010000000003', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.4\"}]}}'),
('001010000000004', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.5\"}]}}'),
('001010000000005', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.6\"}]}}'),
('001010000000006', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.7\"}]}}'),
('001010000000007', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.8\"}]}}'),
('001010000000008', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.9\"}]}}'),
('001010000000009', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.10\"}]}}'),
('001010000000010', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.11\"}]}}'),
('001010000000011', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}', '{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.12\"}]}}'),
('001010000000012', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.13\"}]}}'),
('001010000000013', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.14\"}]}}'),
('001010000000014', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.15\"}]}}'),
('001010000000015', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.16\"}]}}'),
('001010000000016', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.17\"}]}}'),
('001010000000017', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.18\"}]}}'),
('001010000000018', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.19\"}]}}'),
('001010000000019', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.20\"}]}}'),
('001010000000020', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.21\"}]}}'),
('001010000000021', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.22\"}]}}'),
('001010000000022', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.23\"}]}}'),
('001010000000023', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.24\"}]}}'),
('001010000000024', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.25\"}]}}'),
('001010000000025', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.26\"}]}}'),
('001010000000026', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.27\"}]}}'),
('001010000000027', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.28\"}]}}'),
('001010000000028', '00101', '{\"sst\": 1, \"sd\": \"FFFFFF\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 9,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"12.1.1.29\"}]}}')
ON DUPLICATE KEY UPDATE 
  dnnConfigurations=VALUES(dnnConfigurations);

COMMIT;