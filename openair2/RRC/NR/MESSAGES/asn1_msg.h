/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.1  (the "License"); you may not use this file
 * except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.openairinterface.org/?page_id=698
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */

/*! \file asn1_msg.h
* \brief primitives to build the asn1 messages
* \author Raymond Knopp and Navid Nikaein, WIE-TAI CHEN
* \date 2011, 2018
* \version 1.0
* \company Eurecom, NTUST
* \email: raymond.knopp@eurecom.fr and  navid.nikaein@eurecom.fr, kroempa@gmail.com
*/

#ifndef __RRC_NR_MESSAGES_ASN1_MSG__H__
#define __RRC_NR_MESSAGES_ASN1_MSG__H__

#include <common/utils/assertions.h>
#include <stdint.h>
#include <stdio.h>
#include "NR_ARFCN-ValueNR.h"
#include "NR_CellGroupConfig.h"
#include "NR_CipheringAlgorithm.h"
#include "NR_DRB-ToAddModList.h"
#include "NR_DRB-ToReleaseList.h"
#include "NR_IntegrityProtAlgorithm.h"
#include "NR_LogicalChannelConfig.h"
#include "NR_MeasConfig.h"
#include "NR_MeasTiming.h"
#include "NR_RLC-BearerConfig.h"
#include "NR_RLC-Config.h"
#include "NR_RRC-TransactionIdentifier.h"
#include "NR_ResumeCause.h"
#include "NR_RadioBearerConfig.h"
#include "NR_ReestablishmentCause.h"
#include "NR_SRB-ToAddModList.h"
#include "NR_SecurityConfig.h"
#include "NR_MeasurementReport.h"
#include "NR_MeasurementTimingConfiguration.h"
#include "NR_PCCH-Config.h"
#include "NR_UE-CapabilityRAT-ContainerList.h"
#include "ds/seq_arr.h"
#include "ds/byte_array.h"
#include "rrc_messages_types.h"
#include "openair2/LAYER2/nr_pdcp/nr_pdcp_configuration.h"
#include "common/utils/nr/nr_common.h"
struct asn_TYPE_descriptor_s;

typedef struct {
  uint8_t transaction_id;
  NR_SRB_ToAddModList_t *srb_config_list;
  NR_DRB_ToAddModList_t *drb_config_list;
  int *drb_rel;
  int n_drb_rel;
  NR_SecurityConfig_t *security_config;
  NR_MeasConfig_t *meas_config;
  byte_array_t dedicated_NAS_msg_list[MAX_DRBS_PER_UE];
  int num_nas_msg;
  NR_CellGroupConfig_t *cell_group_config;
  bool masterKeyUpdate;
  int nextHopChainingCount;
  byte_array_t ue_cap;
} nr_rrc_reconfig_param_t;

/*
 * The variant of the above function which dumps the BASIC-XER (XER_F_BASIC)
 * output into the chosen string buffer.
 * RETURN VALUES:
 *       0: The structure is printed.
 *      -1: Problem printing the structure.
 * WARNING: No sensible errno value is returned.
 */
int xer_sprint_NR(char *string, size_t string_size, struct asn_TYPE_descriptor_s *td, void *sptr);

int do_SIB2_NR(uint8_t **msg_SIB2, NR_SSB_MTC_t *ssbmtc);

int do_RRCReject(uint8_t *const buffer);

int do_RRCSetup(uint8_t *const buffer,
                size_t buffer_size,
                const uint8_t transaction_id,
                const uint8_t *masterCellGroup,
                int masterCellGroup_len,
                const gNB_RrcConfigurationReq *configuration,
                NR_SRB_ToAddModList_t *SRBs);

int do_NR_SecurityModeCommand(uint8_t *const buffer,
                              const uint8_t Transaction_id,
                              const uint8_t cipheringAlgorithm,
                              NR_IntegrityProtAlgorithm_t integrityProtAlgorithm);

int do_NR_SA_UECapabilityEnquiry(uint8_t *const buffer, const uint8_t Transaction_id);

int do_NR_RRCRelease(uint8_t *buffer, size_t buffer_size, uint8_t Transaction_id);

int do_NR_RRCRelease_suspend(uint8_t *buffer,
                             size_t buffer_size,
                             uint8_t Transaction_id,
                             uint64_t full_i_rnti,
                             uint32_t short_i_rnti);

byte_array_t do_RRCReconfiguration(const nr_rrc_reconfig_param_t *params);

int do_RRCSetupComplete(uint8_t *buffer,
                        size_t buffer_size,
                        const uint8_t Transaction_id,
                        uint8_t sel_plmn_id,
                        bool is_rrc_connection_setup,
                        uint64_t fiveG_S_TMSI,
                        const int dedicatedInfoNASLength,
                        const char *dedicatedInfoNAS);

int do_NR_HandoverPreparationInformation(const uint8_t *uecap_buf, int uecap_buf_size, uint8_t *buf, int buf_size);

int do_NR_MeasConfig(const NR_MeasConfig_t *measconfig, uint8_t *buf, int buf_size);

int do_NR_MeasurementTimingConfiguration(const NR_MeasurementTimingConfiguration_t *mtc, uint8_t *buf, int buf_size);

int do_RRCSetupRequest(uint8_t *buffer, size_t buffer_size, uint8_t *rv, uint64_t fiveG_S_TMSI_part1);

int do_nrMeasurementReport_SA(long trigger_to_measid,
                              long trigger_quantity,
                              long rs_type,
                              uint16_t Nid_cell,
                              int rsrp_index,
                              uint8_t *buffer,
                              size_t buffer_size);

int do_NR_RRCReconfigurationComplete_for_nsa(uint8_t *buffer, size_t buffer_size, NR_RRC_TransactionIdentifier_t Transaction_id);

int do_NR_RRCReconfigurationComplete(uint8_t *buffer, size_t buffer_size, const uint8_t Transaction_id);

int do_NR_RRCResume(uint8_t *buffer, size_t buffer_size, const uint8_t Transaction_id);

int do_NR_RRCResumeComplete(uint8_t *buffer, size_t buffer_size, const uint8_t Transaction_id);

int do_NR_RRCResumeRequest(uint8_t *buffer, size_t buffer_size, uint32_t short_i_rnti, NR_ResumeCause_t resume_cause);

int do_NR_DLInformationTransfer(uint8_t *buffer,
                                size_t buffer_len,
                                uint8_t transaction_id,
                                uint32_t pdu_length,
                                uint8_t *pdu_buffer);

int do_NR_ULInformationTransfer(uint8_t **buffer,
                                uint32_t pdu_length,
                                uint8_t *pdu_buffer);

int do_RRCReestablishmentRequest(uint8_t *buffer,
                                 NR_ReestablishmentCause_t cause,
                                 uint32_t cell_id,
                                 uint16_t c_rnti);

int do_RRCReestablishment(int8_t nh_ncc, uint8_t *const buffer, size_t buffer_size, const uint8_t Transaction_id);

int do_RRCReestablishmentComplete(uint8_t *buffer, size_t buffer_size, int64_t rrc_TransactionIdentifier);

NR_MeasConfig_t *get_MeasConfig(const NR_MeasTiming_t *mt,
                                int band,
                                int scs,
                                int nr_pci,
                                NR_ReportConfigToAddMod_t *rc_PER,
                                NR_ReportConfigToAddMod_t *rc_A2,
                                seq_arr_t *rc_A3_seq,
                                seq_arr_t *neigh_seq);
void free_MeasConfig(NR_MeasConfig_t *mc);
int do_NR_Paging(uint8_t Mod_id, uint8_t *buffer, uint32_t tmsi);

typedef struct {
  uint32_t cycle_frames;
  uint32_t paging_frames;
  uint32_t paging_frame_offset;
  uint32_t paging_occasions;
} nr_rrc_paging_parameters_t;

typedef struct {
  uint16_t paging_frame;
  uint32_t paging_occasion;
} nr_rrc_paging_occasion_t;

typedef enum {
  NR_RRC_PAGING_ERROR = -1,
  NR_RRC_PAGING_NOT_OCCASION = 0,
  NR_RRC_PAGING_OCCASION = 1,
} nr_rrc_paging_occasion_status_t;

enum {
  NR_RRC_PAGING_PARAMETERS_OK = 0,
  NR_RRC_PAGING_SFN_COUNT = 1024,
  NR_RRC_PAGING_UE_ID_MODULUS = NR_RRC_PAGING_SFN_COUNT,
  NR_RRC_PAGING_SEARCH_SPACE_UNCONFIGURED = -1,
  NR_RRC_PAGING_FIRST_SEARCH_SPACE_ID = 1,
  NR_RRC_PAGING_NO_FRAME_OFFSET = 0,
  NR_RRC_PAGING_FIRST_OCCASION = 0,
  NR_RRC_PAGING_NS_ONE = 1,
  NR_RRC_PAGING_NS_TWO = 2,
  NR_RRC_PAGING_NS_FOUR = 4,
  NR_RRC_PAGING_CYCLE_COUNT = NR_PagingCycle_rf256 + 1,
};

/** @brief Decode PF/PO parameters from the NR PCCH configuration.
 *  @param pcch_config NR PCCH configuration from SIB1.
 *  @param paging_search_space Configured paging search-space ID, or the unconfigured sentinel.
 *  @param paging_drx UE default paging-cycle index.
 *  @param parameters Output PF/PO parameters.
 *  @return NR_RRC_PAGING_PARAMETERS_OK or NR_RRC_PAGING_ERROR. */
int nr_rrc_get_paging_parameters(const NR_PCCH_Config_t *pcch_config,
                                 long paging_search_space,
                                 uint8_t paging_drx,
                                 nr_rrc_paging_parameters_t *parameters);

/** @brief Evaluate the TS 38.304 PF/PO identity for one SFN.
 *  @param pcch_config NR PCCH configuration from SIB1.
 *  @param paging_search_space Configured paging search-space ID, or the unconfigured sentinel.
 *  @param paging_drx UE default paging-cycle index.
 *  @param fiveg_s_tmsi UE 5G-S-TMSI used for UE_ID.
 *  @param sfn System frame number to evaluate.
 *  @param occasion Output PF/PO identity.
 *  @return NR_RRC_PAGING_OCCASION, NR_RRC_PAGING_NOT_OCCASION, or NR_RRC_PAGING_ERROR. */
nr_rrc_paging_occasion_status_t nr_rrc_get_paging_occasion(const NR_PCCH_Config_t *pcch_config,
                                                           long paging_search_space,
                                                           uint8_t paging_drx,
                                                           uint32_t fiveg_s_tmsi,
                                                           uint16_t sfn,
                                                           nr_rrc_paging_occasion_t *occasion);

byte_array_t get_HandoverPreparationInformation(nr_rrc_reconfig_param_t *params, int scell_pci);
byte_array_t get_HandoverCommandMessage(nr_rrc_reconfig_param_t *params);
void fill_removal_lists_from_source_measConfig(NR_MeasConfig_t *measConfig, byte_array_t prep_info);
int doRRCReconfiguration_from_HandoverCommand(byte_array_t *ba, byte_array_t handoverCommand);

struct NR_UE_NR_Capability *get_ue_nr_capability(int rnti, uint8_t *buf, uint32_t len);
NR_UE_NR_Capability_t *decode_nr_ue_capability(int rnti, const NR_UE_CapabilityRAT_ContainerList_t *clist);

#endif  /* __RRC_NR_MESSAGES_ASN1_MSG__H__ */
