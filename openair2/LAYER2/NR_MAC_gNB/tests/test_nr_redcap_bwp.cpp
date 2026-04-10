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

extern "C" {
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

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
