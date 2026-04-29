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

#include <cstdlib>

#include <gtest/gtest.h>

extern "C" {
#include "NR_ControlResourceSet.h"
#include "NR_FeatureCombinationPreambles-r17.h"
#include "NR_PDCCH-ConfigCommon.h"
#include "NR_RACH-ConfigCommon.h"
#include "NR_SearchSpace.h"
#include "openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h"
}

static constexpr long kScs15 = 0;
static constexpr long kScs30 = 1;
static constexpr long kScs60 = 2;

TEST(nr_redcap_bwp, fr1_max_prbs_from_scs)
{
  EXPECT_EQ(106, nr_redcap_fr1_max_prbs_from_scs(kScs15));
  EXPECT_EQ(51, nr_redcap_fr1_max_prbs_from_scs(kScs30));
  EXPECT_EQ(-1, nr_redcap_fr1_max_prbs_from_scs(kScs60));
}

TEST(nr_redcap_bwp, requested_detects_partial_configuration)
{
  EXPECT_FALSE(nr_redcap_initial_bwp_requested(-1, -1, -1));
  EXPECT_TRUE(nr_redcap_initial_bwp_requested(0, -1, -1));
  EXPECT_TRUE(nr_redcap_initial_bwp_requested(-1, 51, -1));
  EXPECT_TRUE(nr_redcap_initial_bwp_requested(-1, -1, kScs30));
}

TEST(nr_redcap_bwp, configure_uses_common_fallbacks)
{
  nr_redcap_bwp_config_t cfg = {};
  nr_redcap_configure_initial_bwp(&cfg, "DL", 0, 51, kScs30, 10, 0, -1, -1, 106);

  EXPECT_TRUE(cfg.configured);
  EXPECT_EQ(0, cfg.bwp_start);
  EXPECT_EQ(51, cfg.bwp_size);
  EXPECT_EQ(10, cfg.controlResourceSetZero);
  EXPECT_EQ(0, cfg.searchSpaceZero);
  EXPECT_EQ(13750, cfg.location_and_bw);
}

TEST(nr_redcap_bwp, configure_uses_explicit_overrides)
{
  nr_redcap_bwp_config_t cfg = {};
  nr_redcap_configure_initial_bwp(&cfg, "UL", 0, 51, kScs30, 5, -1, 7, -1, 106);

  EXPECT_TRUE(cfg.configured);
  EXPECT_EQ(7, cfg.pucch_ResourceCommonRedCap_r17);
  EXPECT_EQ(7, cfg.controlResourceSetZero);
  EXPECT_EQ(-1, cfg.searchSpaceZero);
  EXPECT_EQ(13750, cfg.location_and_bw);
}

TEST(nr_redcap_bwp, configure_rejects_invalid_scs)
{
  nr_redcap_bwp_config_t cfg = {};
  ASSERT_DEATH({ nr_redcap_configure_initial_bwp(&cfg, "DL", 0, 51, kScs60, 10, 0, -1, -1, 106); },
               "only supports FR1 SCS 15/30 kHz");
}

TEST(nr_redcap_bwp, configure_rejects_oversized_20mhz_bwp)
{
  nr_redcap_bwp_config_t cfg = {};
  ASSERT_DEATH({ nr_redcap_configure_initial_bwp(&cfg, "DL", 0, 52, kScs30, 10, 0, -1, -1, 106); },
               "exceeds the FR1 20 MHz limit");
}

TEST(nr_redcap_bwp, case_b_requires_edge_alignment)
{
  nr_redcap_bwp_config_t cfg = {
      .configured = true,
      .bwp_start = 10,
      .bwp_size = 51,
  };
  ASSERT_DEATH({ nr_redcap_validate_coreset0_dl_bwp(NR_REDCAP_CORESET0_MODE_CASE_B, &cfg, 106); },
               "requires an edge-aligned initial DL BWP");
}

TEST(nr_redcap_bwp, case_b_accepts_edge_aligned_bwp)
{
  nr_redcap_bwp_config_t cfg = {
      .configured = true,
      .bwp_start = 55,
      .bwp_size = 51,
  };
  nr_redcap_validate_coreset0_dl_bwp(NR_REDCAP_CORESET0_MODE_CASE_B, &cfg, 106);
}

TEST(nr_redcap_bwp, case_b_conversion_rebinds_common_searchspaces_and_clears_type0_css)
{
  NR_PDCCH_ConfigCommon_t pdcch_cc = {};
  pdcch_cc.controlResourceSetZero = static_cast<long *>(calloc(1, sizeof(*pdcch_cc.controlResourceSetZero)));
  pdcch_cc.searchSpaceZero = static_cast<long *>(calloc(1, sizeof(*pdcch_cc.searchSpaceZero)));
  pdcch_cc.searchSpaceSIB1 = static_cast<long *>(calloc(1, sizeof(*pdcch_cc.searchSpaceSIB1)));
  pdcch_cc.commonSearchSpaceList =
      static_cast<decltype(pdcch_cc.commonSearchSpaceList)>(calloc(1, sizeof(*pdcch_cc.commonSearchSpaceList)));
  ASSERT_NE(pdcch_cc.controlResourceSetZero, nullptr);
  ASSERT_NE(pdcch_cc.searchSpaceZero, nullptr);
  ASSERT_NE(pdcch_cc.searchSpaceSIB1, nullptr);
  ASSERT_NE(pdcch_cc.commonSearchSpaceList, nullptr);

  auto *ss0 = static_cast<NR_SearchSpace_t *>(calloc(1, sizeof(NR_SearchSpace_t)));
  auto *ss1 = static_cast<NR_SearchSpace_t *>(calloc(1, sizeof(NR_SearchSpace_t)));
  ASSERT_NE(ss0, nullptr);
  ASSERT_NE(ss1, nullptr);
  ss1->controlResourceSetId = static_cast<long *>(calloc(1, sizeof(*ss1->controlResourceSetId)));
  ASSERT_NE(ss1->controlResourceSetId, nullptr);
  *ss1->controlResourceSetId = 3;
  ASSERT_EQ(0, ASN_SEQUENCE_ADD(&pdcch_cc.commonSearchSpaceList->list, ss0));
  ASSERT_EQ(0, ASN_SEQUENCE_ADD(&pdcch_cc.commonSearchSpaceList->list, ss1));

  auto *common_coreset = static_cast<NR_ControlResourceSet_t *>(calloc(1, sizeof(NR_ControlResourceSet_t)));
  ASSERT_NE(common_coreset, nullptr);
  common_coreset->controlResourceSetId = 7;

  nr_redcap_apply_case_b_common_coreset(&pdcch_cc, common_coreset);

  EXPECT_EQ(nullptr, pdcch_cc.controlResourceSetZero);
  EXPECT_EQ(nullptr, pdcch_cc.searchSpaceZero);
  EXPECT_EQ(nullptr, pdcch_cc.searchSpaceSIB1);
  ASSERT_EQ(common_coreset, pdcch_cc.commonControlResourceSet);
  ASSERT_EQ(2, pdcch_cc.commonSearchSpaceList->list.count);
  ASSERT_NE(pdcch_cc.commonSearchSpaceList->list.array[0]->controlResourceSetId, nullptr);
  ASSERT_NE(pdcch_cc.commonSearchSpaceList->list.array[1]->controlResourceSetId, nullptr);
  EXPECT_EQ(7, *pdcch_cc.commonSearchSpaceList->list.array[0]->controlResourceSetId);
  EXPECT_EQ(7, *pdcch_cc.commonSearchSpaceList->list.array[1]->controlResourceSetId);

  free(ss0->controlResourceSetId);
  free(ss0);
  free(ss1->controlResourceSetId);
  free(ss1);
  free(pdcch_cc.commonSearchSpaceList->list.array);
  free(pdcch_cc.commonSearchSpaceList);
  free(pdcch_cc.commonControlResourceSet);
}

TEST(nr_redcap_bwp, case_b_conversion_requires_common_searchspace_list)
{
  NR_PDCCH_ConfigCommon_t pdcch_cc = {};
  auto *common_coreset = static_cast<NR_ControlResourceSet_t *>(calloc(1, sizeof(NR_ControlResourceSet_t)));
  ASSERT_NE(common_coreset, nullptr);
  common_coreset->controlResourceSetId = 9;

  ASSERT_DEATH({ nr_redcap_apply_case_b_common_coreset(&pdcch_cc, common_coreset); }, "requires commonSearchSpaceList");
  free(common_coreset);
}

TEST(nr_redcap_bwp, rach_feature_partition_adds_redcap_tail_preambles)
{
  NR_RACH_ConfigCommon_t rach = {};

  nr_redcap_configure_rach_feature_combination_preambles(&rach);

  ASSERT_NE(rach.ext2, nullptr);
  ASSERT_NE(rach.ext2->featureCombinationPreamblesList_r17, nullptr);
  ASSERT_EQ(1, rach.ext2->featureCombinationPreamblesList_r17->list.count);
  const NR_FeatureCombinationPreambles_r17_t *partition = rach.ext2->featureCombinationPreamblesList_r17->list.array[0];
  ASSERT_NE(partition, nullptr);
  ASSERT_NE(partition->featureCombination_r17.redCap_r17, nullptr);
  EXPECT_EQ(NR_FeatureCombination_r17__redCap_r17_true, *partition->featureCombination_r17.redCap_r17);
  EXPECT_EQ(60, partition->startPreambleForThisPartition_r17);
  EXPECT_EQ(4, partition->numberOfPreamblesPerSSB_ForThisPartition_r17);

  free(partition->featureCombination_r17.redCap_r17);
  free(const_cast<NR_FeatureCombinationPreambles_r17_t *>(partition));
  free(rach.ext2->featureCombinationPreamblesList_r17->list.array);
  free(rach.ext2->featureCombinationPreamblesList_r17);
  free(rach.ext2);
}

TEST(nr_redcap_bwp, rach_feature_partition_honors_total_preambles)
{
  NR_RACH_ConfigCommon_t rach = {};
  long total_preambles = 16;
  rach.totalNumberOfRA_Preambles = &total_preambles;

  nr_redcap_configure_rach_feature_combination_preambles(&rach);

  ASSERT_EQ(1, rach.ext2->featureCombinationPreamblesList_r17->list.count);
  const NR_FeatureCombinationPreambles_r17_t *partition = rach.ext2->featureCombinationPreamblesList_r17->list.array[0];
  EXPECT_EQ(12, partition->startPreambleForThisPartition_r17);
  EXPECT_EQ(4, partition->numberOfPreamblesPerSSB_ForThisPartition_r17);

  free(partition->featureCombination_r17.redCap_r17);
  free(const_cast<NR_FeatureCombinationPreambles_r17_t *>(partition));
  free(rach.ext2->featureCombinationPreamblesList_r17->list.array);
  free(rach.ext2->featureCombinationPreamblesList_r17);
  free(rach.ext2);
}

TEST(nr_redcap_bwp, rach_feature_partition_is_idempotent)
{
  NR_RACH_ConfigCommon_t rach = {};

  nr_redcap_configure_rach_feature_combination_preambles(&rach);
  nr_redcap_configure_rach_feature_combination_preambles(&rach);

  EXPECT_EQ(1, rach.ext2->featureCombinationPreamblesList_r17->list.count);

  NR_FeatureCombinationPreambles_r17_t *partition = rach.ext2->featureCombinationPreamblesList_r17->list.array[0];
  free(partition->featureCombination_r17.redCap_r17);
  free(partition);
  free(rach.ext2->featureCombinationPreamblesList_r17->list.array);
  free(rach.ext2->featureCombinationPreamblesList_r17);
  free(rach.ext2);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
