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

#include <gtest/gtest.h>
#ifdef __cplusplus
extern "C" {
#endif
#include "openair2/RRC/NR/MESSAGES/asn1_msg.h"
#include "openair3/AIOTF/aiotf_inventory.h"
#include "common/ran_context.h"
#include <stdbool.h>
#include "common/utils/assertions.h"
#include "common/utils/LOG/log.h"
#include "NR_DRB-ToAddMod.h"
#include "NR_DRB-ToAddModList.h"
#include "NR_SRB-ToAddModList.h"
#include "ds/byte_array.h"
RAN_CONTEXT_t RC;
#ifdef __cplusplus
}
#endif

TEST(nr_asn1, rrc_reject)
{
  unsigned char buf[1000];
  EXPECT_GT(do_RRCReject(buf), 0);
}

TEST(nr_asn1, sa_capability_enquiry)
{
  unsigned char buf[1000];
  EXPECT_GT(do_NR_SA_UECapabilityEnquiry(buf, 0), 0);
}

TEST(nr_asn1, rrc_reconfiguration_complete_for_nsa)
{
  unsigned char buf[1000];
  EXPECT_GT(do_NR_RRCReconfigurationComplete_for_nsa(buf, 1000, 0), 0);
}

TEST(nr_asn1, ul_information_transfer)
{
  unsigned char *buf = NULL;
  unsigned char pdu[20] = {0};
  EXPECT_GT(do_NR_ULInformationTransfer(&buf, 20, pdu), 0);
  EXPECT_NE(buf, nullptr);
  free(buf);
}

TEST(nr_asn1, rrc_reestablishment_request)
{
  unsigned char buf[1000];
  const uint16_t c_rnti = 1;
  const uint32_t cell_id = 177;
  EXPECT_GT(do_RRCReestablishmentRequest(buf, NR_ReestablishmentCause_reconfigurationFailure, cell_id, c_rnti), 0);
}

TEST(nr_asn1, rrc_reestablishment)
{
  unsigned char buf[1000];
  const uint8_t nh_ncc = 0;
  EXPECT_GT(do_RRCReestablishment(nh_ncc, buf, 1000, 0), 0);
}

TEST(nr_asn1, paging)
{
  unsigned char buf[1000];
  EXPECT_GT(do_NR_Paging(0, buf, 0), 0);
}

TEST(nr_asn1, paging_occasion_timeout)
{
  constexpr uint32_t kFivegSTmsi = 1;
  constexpr uint32_t kTagId = 1;
  constexpr uint32_t kConfiguredCycleFrames = 32;
  constexpr uint16_t kPagingSfn = 97;
  constexpr uint16_t kFrameStep = 1;
  constexpr uint64_t kRadioFrameDurationMs = 10;
  constexpr uint32_t kAiotfTimeoutMs = 100;
  constexpr long kPagingSearchSpaceId = 1;
  constexpr uint8_t kPagingDrx = NR_PagingCycle_rf32;
  constexpr long kQuarterTOffset = 2;
  constexpr uint16_t kQuarterTPagingSfn = 2;
  constexpr uint32_t kQuarterTDivisor = 4;
  constexpr uint64_t kDeadlineStepMs = 1;

  NR_PCCH_Config_t pcch = {};
  pcch.defaultPagingCycle = NR_PagingCycle_rf32;
  pcch.nAndPagingFrameOffset.present = NR_PCCH_Config__nAndPagingFrameOffset_PR_oneT;
  pcch.ns = NR_PCCH_Config__ns_one;

  nr_rrc_paging_occasion_t occasion = {};
  nr_rrc_paging_occasion_t before = {};
  EXPECT_EQ(NR_RRC_PAGING_NOT_OCCASION,
            nr_rrc_get_paging_occasion(&pcch,
                                       kPagingSearchSpaceId,
                                       kPagingDrx,
                                       kFivegSTmsi,
                                       kPagingSfn - kFrameStep,
                                       &before));
  ASSERT_EQ(NR_RRC_PAGING_OCCASION,
            nr_rrc_get_paging_occasion(&pcch,
                                       kPagingSearchSpaceId,
                                       kPagingDrx,
                                       kFivegSTmsi,
                                       kPagingSfn,
                                       &occasion));
  nr_rrc_paging_occasion_t after = {};
  EXPECT_EQ(NR_RRC_PAGING_NOT_OCCASION,
            nr_rrc_get_paging_occasion(&pcch,
                                       kPagingSearchSpaceId,
                                       kPagingDrx,
                                       kFivegSTmsi,
                                       kPagingSfn + kFrameStep,
                                       &after));
  ASSERT_EQ(kPagingSfn, occasion.paging_frame);
  ASSERT_EQ(NR_RRC_PAGING_FIRST_OCCASION, occasion.paging_occasion);

  nr_rrc_paging_occasion_t invalid = {};
  EXPECT_EQ(NR_RRC_PAGING_ERROR,
            nr_rrc_get_paging_occasion(&pcch,
                                       kPagingSearchSpaceId,
                                       kPagingDrx,
                                       kFivegSTmsi,
                                       NR_RRC_PAGING_SFN_COUNT,
                                       &invalid));

  NR_PCCH_Config_t configured_offset_pcch = pcch;
  configured_offset_pcch.nAndPagingFrameOffset.present = NR_PCCH_Config__nAndPagingFrameOffset_PR_quarterT;
  configured_offset_pcch.nAndPagingFrameOffset.choice.quarterT = kQuarterTOffset;
  nr_rrc_paging_parameters_t configured_parameters = {};
  ASSERT_EQ(NR_RRC_PAGING_PARAMETERS_OK,
            nr_rrc_get_paging_parameters(&configured_offset_pcch,
                                         kPagingSearchSpaceId,
                                         kPagingDrx,
                                         &configured_parameters));
  ASSERT_EQ(kConfiguredCycleFrames / kQuarterTDivisor, configured_parameters.paging_frames);
  ASSERT_EQ(kQuarterTOffset, configured_parameters.paging_frame_offset);
  nr_rrc_paging_occasion_t configured_offset = {};
  ASSERT_EQ(NR_RRC_PAGING_OCCASION,
            nr_rrc_get_paging_occasion(&configured_offset_pcch,
                                       kPagingSearchSpaceId,
                                       kPagingDrx,
                                       kFivegSTmsi,
                                       kQuarterTPagingSfn,
                                       &configured_offset));

  /* A radio frame is 10 ms. Ns=1 makes the exposed PF/PO boundary unambiguous. */
  const uint64_t paging_occasion_ms = (uint64_t)occasion.paging_frame * kRadioFrameDurationMs;
  const aiotf_inventory_request_t request = {.tag_id = kTagId, .timeout_ms = kAiotfTimeoutMs};
  aiotf_inventory_context_t context = {};
  aiotf_inventory_session_t session = {};
  aiotf_inventory_context_init(&context);
  ASSERT_EQ(AIOTF_REQUEST_ACCEPTED,
            aiotf_inventory_start(&context, &request, paging_occasion_ms - request.timeout_ms, &session));
  ASSERT_EQ(paging_occasion_ms, session.deadline_ms);
  EXPECT_FALSE(aiotf_inventory_expire(&session, paging_occasion_ms - kDeadlineStepMs));
  EXPECT_TRUE(aiotf_inventory_expire(&session, paging_occasion_ms));
  EXPECT_FALSE(aiotf_inventory_expire(&session, paging_occasion_ms + kDeadlineStepMs));
}

void free_RRCReconfiguration_params(nr_rrc_reconfig_param_t params)
{
  ASN_STRUCT_FREE(asn_DEF_NR_MeasConfig, params.meas_config);
  ASN_STRUCT_FREE(asn_DEF_NR_DRB_ToAddModList, params.drb_config_list);
  ASN_STRUCT_FREE(asn_DEF_NR_SRB_ToAddModList, params.srb_config_list);
  ASN_STRUCT_FREE(asn_DEF_NR_SecurityConfig, params.security_config);
  for (int i = 0; i < params.num_nas_msg; i++)
    FREE_AND_ZERO_BYTE_ARRAY(params.dedicated_NAS_msg_list[i]);
}

TEST(nr_asn1, rrc_reconfiguration)
{
  // SRB Configuration
  NR_SRB_ToAddModList_t *srb_config_list = (NR_SRB_ToAddModList_t *)calloc_or_fail(1, sizeof(*srb_config_list));
  for (int i = 0; i < 4; i++) {
    if (i == 1 || i == 2) {
      NR_SRB_ToAddMod_t *srb = (NR_SRB_ToAddMod_t *)calloc_or_fail(1, sizeof(*srb));
      ASN_SEQUENCE_ADD(&srb_config_list->list, srb);
      srb->srb_Identity = i;
      if (i == 1 || i == 2) {
        srb->reestablishPDCP = (long *)calloc_or_fail(1, sizeof(*srb->reestablishPDCP));
        *srb->reestablishPDCP = 0;
      }
    }
  }

  // DRB Configuration
  NR_DRB_ToAddModList_t *drb_config_list = (NR_DRB_ToAddModList_t *)calloc_or_fail(1, sizeof(*drb_config_list));
  for (int i = 0; i < 32; i++) {
    if (i == 1 || i == 2) {
      NR_DRB_ToAddMod_t *drb = (NR_DRB_ToAddMod_t *)calloc_or_fail(1, sizeof(*drb));
      ASN_SEQUENCE_ADD(&drb_config_list->list, drb);
      drb->drb_Identity = i;
      drb->reestablishPDCP = (long *)calloc_or_fail(1, sizeof(*drb->reestablishPDCP));
      *drb->reestablishPDCP = 0;
    }
  }

  // nr_rrc_reconfig_param_t setup
  nr_rrc_reconfig_param_t params = {};
  params.srb_config_list = srb_config_list;
  params.drb_config_list = drb_config_list;
  params.num_nas_msg = 2;
  params.masterKeyUpdate = false;
  params.nextHopChainingCount = 1;

  byte_array_t nas_pdu_1;
  nas_pdu_1.buf = (uint8_t *)malloc_or_fail(4);
  memcpy(nas_pdu_1.buf, "NAS1", 4);
  nas_pdu_1.len = 4;

  byte_array_t nas_pdu_2;
  nas_pdu_2.buf = (uint8_t *)malloc_or_fail(4);
  memcpy(nas_pdu_2.buf, "NAS2", 4);
  nas_pdu_2.len = 4;

  params.dedicated_NAS_msg_list[0] = nas_pdu_1;
  params.dedicated_NAS_msg_list[1] = nas_pdu_2;

  byte_array_t msg = do_RRCReconfiguration(&params);

  EXPECT_GT(msg.len, 0);
  EXPECT_NE(msg.buf, nullptr);

  LOG_D(NR_RRC, "RRCReconfiguration: Encoded (%ld bytes)\n", msg.len);

  free_byte_array(msg);
  free_RRCReconfiguration_params(params);
}

int main(int argc, char **argv)
{
  logInit();
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
